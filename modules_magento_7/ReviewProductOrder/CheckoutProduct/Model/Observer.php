<?php

include_once('/etc/php5/apache2/xmlrpc.inc'); //http://phpxmlrpc.sourceforge.net
include_once('/etc/php5/apache2/xmlrpcs.inc'); //http://phpxmlrpc.sourceforge.net

require_once('FirePHPCore/fb.php');
ob_start();

class ReviewProductOrder_CheckoutProduct_Model_Observer
{
    /**Magento passes a Varien_Event_Observer object as
     * the first parameter of dispatched events.
     */

    public $user;
    public $password;
    public $database;
    public $url;
    
    public $error_msg;
    
    function __construct($user, $password, $database, $url){
        $this->user = $user;
        $this->password = $password;
        $this->database = $database;
        $this->url = $url;
    }
   
    function login(){
        try{
            $msg = new xmlrpcmsg('login');
            $msg->addParam(new xmlrpcval($this->database, "string"));
            $msg->addParam(new xmlrpcval($this->user, "string"));
            $msg->addParam(new xmlrpcval($this->password, "string"));
            $val = $this->_cache_request($this->url.'common',$msg);
            
            $this->userId = $val->scalarVal();

            if($this->userId > 0) {
                //Mage::getSingleton('checkout/session')->addSuccess("Conection succesuful");
                return $this->userId;
            }
            else{
                //Mage::getSingleton('checkout/session')->addError("Conection failed with Openerp. Check error log"); 
                Mage::log($this->error_msg,null,'sales_order_save_after.log');
                Mage::throwException('Conection failed with Openerp. Check error log');               
                //die();
                return -1;
            }
        }
        catch(Exception $e){
            Mage::log($this->error_msg,null,'sales_order_save_after.log');
            Mage::throwException('Conection failed with Openerp. Check error log');
                   
        }
    }
    
    function search($relation,$domain){
        $msg = new xmlrpcmsg('execute');
        $msg->addParam(new xmlrpcval($this->database, "string"));
        $msg->addParam(new xmlrpcval($this->userId   , "int"));
        $msg->addParam(new xmlrpcval($this->password, "string"));
        $msg->addParam(new xmlrpcval($relation      , "string"));
        $msg->addParam(new xmlrpcval("search"      , "string"));
        $msg->addParam(php_xmlrpc_encode($domain));
        $val = $this->_cache_request($this->url.'object',$msg);
        
        return php_xmlrpc_decode($val);
    }
    
    function read($relation,$ids,$fields=array(),$context=array()){
        $msg = new xmlrpcmsg('execute');
        $msg->addParam(new xmlrpcval($this->database, "string"));
        $msg->addParam(new xmlrpcval($this->userId, "int"));
        $msg->addParam(new xmlrpcval($this->password, "string"));
        $msg->addParam(new xmlrpcval($relation, "string"));
        $msg->addParam(new xmlrpcval("read", "string"));
        $msg->addParam(php_xmlrpc_encode($ids));
        $msg->addParam(php_xmlrpc_encode($fields));
        $val = $this->_cache_request($this->url.'object',$msg);
        
        return php_xmlrpc_decode($val);
    }   
    
    function import_product_out_of_stock_openerp($relation,$product_id,$customer_id,$qty_product,$order_date,$context=array())
    {
        $msg = new xmlrpcmsg('execute');
        $msg->addParam(new xmlrpcval($this->database, "string"));
        $msg->addParam(new xmlrpcval($this->userId, "int"));
        $msg->addParam(new xmlrpcval($this->password, "string"));
        $msg->addParam(new xmlrpcval($relation, "string"));
        $msg->addParam(new xmlrpcval("save_product", "string"));
        $msg->addParam(php_xmlrpc_encode($product_id));
        $msg->addParam(php_xmlrpc_encode($customer_id));
        $msg->addParam(php_xmlrpc_encode($qty_product));
        $msg->addParam(new xmlrpcval($order_date,"string"));
      
        
        $val = $this->_cache_request($this->url.'object',$msg);        
        //return php_xmlrpc_decode($val);
        
    }
    //************************************************** Tools
    function dump_array($arr){
        foreach ($arr as $c) {
            foreach($c as $property => $value)  { 
                
            }
        }
    } 
        
    function _cache_request($url,$msg){
        $key =    md5($url.$msg->serialize());
        $connection = new xmlrpc_client($url);
        $resp = $connection->send($msg);
        $this->error_msg = $resp->faultString();
        $ret = $resp->value();
        return $ret;         
    }
    
    public function main(Varien_Event_Observer $observer){
        $flat = false;
        $message = '';
        $item_info = '';
        $product_model = Mage::getModel('catalog/product'); //getting product model
        
        /**** LOGIN *****/
        $server = new ReviewProductOrder_CheckoutProduct_Model_Observer('admin', 'admin', 'test_electrotech', 'http://127.0.0.1:2001/xmlrpc/');
        $result = $server->login();

        if ($result > -1){
            /****GET ORDER AND ORDER ITEMS **/
            $order = $observer->getEvent()->getOrder();
            $total_items = $order->getTotalItemCount();
        
            //returns an array of order items
            $items = $order->getAllItems();

            if ($items) {
                foreach ($items as $item) {
                    $item_info = $item_info.'Item Name: '.$item['name'].' - Sku: '.$item['sku'].' - Quantity ordered: '.$item['qty_ordered'].' ------ ';
                    
                    /*****search in openerp ****/
                    $ids_products = $server->search('product.product',array(array('default_code','=',$item['sku'])));
                    $products = $server->read('product.product',$ids_products,array('qty_available'));             
                    
                    foreach ($products as $p) {
                        foreach($p as $property => $value){ 
                            if ($property == 'qty_available') {
                                if ($value == 0){
                                    $flat = true;
                                    $message = $item_info.'There is insufficient stock in OpenERP to proceed with this order';          
                                    //************************************************************
                                    $id_product = $item->getProductId();
                                    $customer_id = $order->getCustomerId();
                                    $qty_product = $item['qty_ordered'];
                                    $order_date = $order->getCreatedAtDate();
                                    
                                    $server->import_product_out_of_stock_openerp('magento.stadistic',$id_product,$customer_id,$qty_product,$order_date); 
                                    //*************************************************************                          
                                } 
                            }
                            
                        }
                    }
                }
                if ($flat){                        
                    Mage::throwException($message);
                }  
            }
            else{
                Mage::log('Connection error',null,'info.log');
                Mage::throwException('Connection error !!!');
            }
            
        }
        else{
            Mage::throwException('Conection failed with Openerp. Check error log');
        }
    }
}


?>
