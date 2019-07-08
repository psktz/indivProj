// Initialization as before
var Eth = require('web3-eth');
var eth = new Eth('HTTP://127.0.0.1:7545');

var abi = [{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balances","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"value","type":"uint256"}],"name":"withdraw","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"to","type":"address"},{"name":"value","type":"uint256"}],"name":"transfer","outputs":[{"name":"success","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[{"name":"success","type":"bool"}],"payable":true,"stateMutability":"payable","type":"function"}];

var bytecode = '6060604052341561000f57600080fd5b6101578061001e6000396000f300606060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063cfae321714610046575b600080fd5b341561005157600080fd5b6100596100d4565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561009957808201518184015260208101905061007e565b50505050905090810190601f1680156100c65780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b6100dc610117565b6040805190810160405280600581526020017f48656c6c6f000000000000000000000000000000000000000000000000000000815250905090565b6020604051908101604052806000815250905600a165627a7a7230582025fd22ef32c724ed61b4a388c9fb894d3813ca36bcb56cc7adee9280154fdca10029';

var myAccount = '0x5d407fa205c0233f58efe0a16e77264b30bdf696'

var contract = new web3.eth.Contract(abi);

contract.deploy({data: bytecode})
.send({ // send submits the transaction to the network
    from: myAccount,             // our account
    gas: 1500000,                // how much has we are willing to spend for a transaction
    gasPrice: '30000000000000'
})
.then(function(newContractInstance){ // providing callback to a promise
    console.log(newContractInstance.options.address) // instance with the new contract address
});
