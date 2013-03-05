<?php

# Controllers are not autoloaded so you will have to do it manually:
require_once 'Mage/Customer/controllers/AccountController.php';
include_once('/etc/php5/apache2/xmlrpc.inc'); //http://phpxmlrpc.sourceforge.net
include_once('/etc/php5/apache2/xmlrpcs.inc'); //http://phpxmlrpc.sourceforge.net

class CheckCustomer_CheckCustomerOpenerp_AccountController extends Mage_Customer_AccountController
{
    public $user;
    public $password;
    public $database;
    public $url;
    
    public $error_msg;
    
    
    function setParameters($user, $password, $database, $url){
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
                return $this->userId;
            }
            else{
                Mage::log($this->error_msg,null,'info.log');
                Mage::throwException('Conection failed with Openerp. Check error log');               
                return -1;
            }
        }
        catch(Exception $e){
            Mage::log($this->error_msg,null,'info.log');
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
    
    
    function import_customer_to_openerp($relation,$customer_id,$context=array())
    {
        $msg = new xmlrpcmsg('execute');
        $msg->addParam(new xmlrpcval($this->database, "string"));
        $msg->addParam(new xmlrpcval($this->userId, "int"));
        $msg->addParam(new xmlrpcval($this->password, "string"));
        $msg->addParam(new xmlrpcval($relation, "string"));
        $msg->addParam(new xmlrpcval("import_customers", "string"));
        $msg->addParam(php_xmlrpc_encode($customer_id));
        $val = $this->_cache_request($this->url.'object',$msg);        
        
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
    
    public function createPostAction()
    {
        $session = $this->_getSession();
        if ($session->isLoggedIn()) {
            $this->_redirect('*/*/');
            return;
        }
        $session->setEscapeMessages(true); // prevent XSS injection in user input
        if ($this->getRequest()->isPost()) {
            $errors = array();

            if (!$customer = Mage::registry('current_customer')) {
                $customer = Mage::getModel('customer/customer')->setId(null);
            }

            /* @var $customerForm Mage_Customer_Model_Form */
            $customerForm = Mage::getModel('customer/form');
            $customerForm->setFormCode('customer_account_create')
                ->setEntity($customer);

            $customerData = $customerForm->extractData($this->getRequest());

            if ($this->getRequest()->getParam('is_subscribed', false)) {
                $customer->setIsSubscribed(1);
            }

            /**
             * Initialize customer group id
             */
            $customer->getGroupId();
            $customer_id = $customer->getEntityId();
            Mage::log('Customer id: '.$customer_id,null,'info.log');

            if ($this->getRequest()->getPost('create_address')) {
                /* @var $address Mage_Customer_Model_Address */
                $address = Mage::getModel('customer/address');
                /* @var $addressForm Mage_Customer_Model_Form */
                $addressForm = Mage::getModel('customer/form');
                $addressForm->setFormCode('customer_register_address')
                    ->setEntity($address);

                $addressData    = $addressForm->extractData($this->getRequest(), 'address', false);
                $addressErrors  = $addressForm->validateData($addressData);
                if ($addressErrors === true) {
                    $address->setId(null)
                        ->setIsDefaultBilling($this->getRequest()->getParam('default_billing', false))
                        ->setIsDefaultShipping($this->getRequest()->getParam('default_shipping', false));
                    $addressForm->compactData($addressData);
                    $customer->addAddress($address);

                    $addressErrors = $address->validate();
                    if (is_array($addressErrors)) {
                        $errors = array_merge($errors, $addressErrors);
                    }
                } else {
                    $errors = array_merge($errors, $addressErrors);
                }
            }

            try {
                $customerErrors = $customerForm->validateData($customerData);
                if ($customerErrors !== true) {
                    $errors = array_merge($customerErrors, $errors);
                } else {
                    $customerForm->compactData($customerData);
                    $customer->setPassword($this->getRequest()->getPost('password'));
                    $customer->setConfirmation($this->getRequest()->getPost('confirmation'));
                    $customerErrors = $customer->validate();
                    if (is_array($customerErrors)) {
                        $errors = array_merge($customerErrors, $errors);
                    }
                }

                $validationResult = count($errors) == 0;

                if (true === $validationResult) {
                          
                    $customer->save();                    
                    
                    /*******IMPORT CUSTOMER ******/
                    $server = new CheckCustomer_CheckCustomerOpenerp_AccountController();
                    $server->setParameters('admin', 'admin', 'test_electrotech', 'http://127.0.0.1:2001/xmlrpc/');
                    $result = $server->login();
         
                    if ($result > -1){
                       $customer_id = $customer->getEntityId();
                       $server->import_customer_to_openerp('sneldev.magento',$customer_id);
                    }
                    else{
                        Mage::log('ERROR',null,'info.log');
                        Mage::throwException('Connection error with Openerp. Check the error log.');
                    }
                    /******************************/
                    
                    Mage::dispatchEvent('customer_register_success',
                        array('account_controller' => $this, 'customer' => $customer)
                    );

                    if ($customer->isConfirmationRequired()) {
                        $customer->sendNewAccountEmail(
                            'confirmation',
                            $session->getBeforeAuthUrl(),
                            Mage::app()->getStore()->getId()
                        );
                        $session->addSuccess($this->__('Account confirmation is required. Please, check your email for the confirmation link. To resend the confirmation email please <a href="%s">click here</a>.', Mage::helper('customer')->getEmailConfirmationUrl($customer->getEmail())));
                        $this->_redirectSuccess(Mage::getUrl('*/*/index', array('_secure'=>true)));
                        return;
                    } else {
                        $session->setCustomerAsLoggedIn($customer);
                        $url = $this->_welcomeCustomer($customer);
                        $this->_redirectSuccess($url);
                        return;
                    }
                } else {
                    $session->setCustomerFormData($this->getRequest()->getPost());
                    if (is_array($errors)) {
                        foreach ($errors as $errorMessage) {
                            $session->addError($errorMessage);
                        }
                    } else {
                        $session->addError($this->__('Invalid customer data'));
                    }
                }
            } catch (Mage_Core_Exception $e) {
                $session->setCustomerFormData($this->getRequest()->getPost());
                if ($e->getCode() === Mage_Customer_Model_Customer::EXCEPTION_EMAIL_EXISTS) {
                    $url = Mage::getUrl('customer/account/forgotpassword');
                    $message = $this->__('There is already an account with this email address. If you are sure that it is your email address, <a href="%s">click here</a> to get your password and access your account.', $url);
                    $session->setEscapeMessages(false);
                } else {
                    $message = $e->getMessage();
                }
                $session->addError($message);
            } catch (Exception $e) {
                $session->setCustomerFormData($this->getRequest()->getPost())
                    ->addException($e, $this->__('Cannot save the customer.'));
            }
        }

        $this->_redirectError(Mage::getUrl('*/*/create', array('_secure' => true))); 
              
    }
}

?>
