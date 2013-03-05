<?php

include_once('/etc/php5/apache2/xmlrpc.inc'); //http://phpxmlrpc.sourceforge.net
include_once('/etc/php5/apache2/xmlrpcs.inc'); //http://phpxmlrpc.sourceforge.net

class ImportOrderToOpenerp_ImportOrder_Model_Observer
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
    
    
    function import_order_to_magento_openerp($relation,$entity_id,$increment_id,$context=array())
    {
        $msg = new xmlrpcmsg('execute');
        $msg->addParam(new xmlrpcval($this->database, "string"));
        $msg->addParam(new xmlrpcval($this->userId, "int"));
        $msg->addParam(new xmlrpcval($this->password, "string"));
        $msg->addParam(new xmlrpcval($relation, "string"));
        $msg->addParam(new xmlrpcval("import_orders", "string"));
        $msg->addParam(php_xmlrpc_encode($entity_id));
        $msg->addParam(php_xmlrpc_encode($increment_id));
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
    
    function varDumpToString ($var){
        ob_start();
        var_dump($var);
        $result = ob_get_clean();
        return $result;
    }
        
    function _cache_request($url,$msg){
        $key =    md5($url.$msg->serialize());
        $connection = new xmlrpc_client($url);
        $resp = $connection->send($msg);
        $this->error_msg = $resp->faultString();
        $ret = $resp->value();
        return $ret;         
    }

    public function main_import_openerp(Varien_Event_Observer $observer){

        /**** LOGIN *****/
        $server = new ImportOrderToOpenerp_ImportOrder_Model_Observer('admin', 'admin', 'test_electrotech', 'http://127.0.0.1:2001/xmlrpc/');
        $result = $server->login();
         
        if ($result > -1){
            $event = $observer->getEvent();
            $order = $event->getOrder();
            
            $entity_id = $order->getData('entity_id');
            $increment_id = $order->getData('increment_id');
            
            $server->import_order_to_magento_openerp('sneldev.magento',$entity_id,$increment_id); 
                       
        }
        else{
            Mage::log('ERROR',null,'sales_order_save_after.log');
            Mage::throwException('Error !!! Check the error log.');
        }
        
    }

}


?>
