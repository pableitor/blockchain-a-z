//jbcoins ICO

//Versión del compilador
pragma solidity ^0.4.26;

contract jbcoin_ico {
    
   // num maximo de jbcoins disponibles para venta
   uint public max_jbcoins = 1000000;
   
   // Conversion rate USD/jbcoins
   uint public USD_to_jbcoins = 1000;
    
    //numero total de jbcoins compradas por inversores
    uint public total_jbcoins_bought = 0;
    
    //Mapping del equity del inversor (USD y jbcoins) a su clave publica 
    mapping(address => uint ) equity_jbcoins;
    mapping(address => uint ) equity_usd;

    //Comprobar si un inversor puede comprar jbcoins
    modifier can_buy_jbcoins(uint usd_invested){
        require (usd_invested * USD_to_jbcoins + total_jbcoins_bought <= max_jbcoins);
        _; 
    }
    
    //Comprobar si un inversor puede vender jbcoins
    modifier can_sell_jbcoins(uint jbcoins_sold){
        require (jbcoins_sold <= total_jbcoins_bought);
        _; 
    }
    
    //Obtener balance jbcoins de un inversor a partir de su direccion (external constant)
    function equity_in_jbcoins(address investor) external constant returns(uint){
        return equity_jbcoins[investor];
    }
    
    //Obtener balance USD de un inversor
    function equity_in_usd(address investor) external constant returns(uint){
        return equity_usd[investor];
    }  
    
    //Comprar jbcoins
    function buy_jbcoins(address investor, uint usd_invested) external 
    can_buy_jbcoins(usd_invested) { //aplicamos modificador antes del cuerpo de la funcion
        uint jbcoins_bought = usd_invested * USD_to_jbcoins;
        equity_jbcoins[investor] += jbcoins_bought;
        equity_usd[investor] = equity_jbcoins[investor] / USD_to_jbcoins;
        total_jbcoins_bought += jbcoins_bought;
    }
    
    // Vender jbcoins
    function sell_jbcoins(address investor, uint jbcoins_sold) external 
    can_sell_jbcoins(jbcoins_sold) { //aplicamos modificador antes del cuerpo de la funcion
        equity_jbcoins[investor] -= jbcoins_sold;
        equity_usd[investor] = equity_jbcoins[investor] / USD_to_jbcoins;
        total_jbcoins_bought -= jbcoins_sold;
    }
    
}
