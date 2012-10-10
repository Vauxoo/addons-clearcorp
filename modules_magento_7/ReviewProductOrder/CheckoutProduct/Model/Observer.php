<?php

include_once('/etc/php5/apache2/xmlrpc.inc'); //http://phpxmlrpc.sourceforge.net
include_once('/etc/php5/apache2/xmlrpcs.inc'); //http://phpxmlrpc.sourceforge.net

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
                    $item_info = 'Item Name:'.$item['name'].' - Sku: '.$item['sku'].' - Quantity ordered: '.$item['qty_ordered'];
                    
                    /*****search in openerp ****/
                    $ids_products = $server->search('product.product',array(array('default_code','=',$item['sku'])));
                    $products = $server->read('product.product',$ids_products,array('qty_available'));             
                    
                    foreach ($products as $p) {
                        foreach($p as $property => $value){ 
                            if ($property == 'qty_available') {
                                if ($value == 0){
                                    $flat = true;
                                    $message = $item_info.' There is insufficient stock in OpenERP to proceed with this order';
                                    break;
                                } 
                            }
                            
                        }
                    }
                    
                    /*** SI LOS PRODUCTOS ESTAN CORRECTOS, SE VERIFICA EL CRÉDITO DEL CLIENTE PARA REALIZAR SU COMPRA ****/
                    if ($flat){
                        Mage::throwException($message);
                    }  
                    
                    else{
                        Mage::log('No existe error en los productos',null,'sales_order_save_after.log');
                    }
                    
                }
            }
            else{
                Mage::log('NO CONECTO',null,'sales_order_save_after.log');
                Mage::throwException('No se pueden revisar los productos, error !!!');
            }
            
        }
        else{
            Mage::throwException('Conection failed with Openerp. Check error log');
        }
    }
}


?>
