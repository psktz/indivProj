pragma solidity ^0.5.8;

contract BasicContract {


    mapping (address => uint256) public balances;

    function deposit() public payable returns(bool success) {
        balances[msg.sender] += msg.value;
        return true;
    }

    function withdraw(uint value) public returns(bool success) {
        if(balances[msg.sender] < value) revert();
        balances[msg.sender] -= value;
        msg.sender.transfer(value);
        return true;
    }

    function transfer(address payable to, uint value) public returns(bool success) {
        if(balances[msg.sender] < value) revert();
        balances[msg.sender] -= value;
        to.transfer(value);
        return true;
    }
}