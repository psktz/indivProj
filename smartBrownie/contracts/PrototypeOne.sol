pragma solidity ^ 0.5 .7;

import "./ABDKMathQuad.sol";


//import "github.com/abdk-consulting/abdk-libraries-solidity/ABDKMathQuad.sol";

contract PrototypeContract {

    using ABDKMathQuad for *;
    mapping(address => uint8) public buyers;
    address payable[] buyersArray;

    struct cleanClaimant {
        address payable claimAddress;
        uint sizeOfBet;
    }

    struct advClaimant {
        address payable claimAddress;
        string adversarialGenMethod;
        uint sizeOfBet;
    }

    cleanClaimant[] public cleanClaimantArray;
    advClaimant[] public advClaimantArray;

    mapping(address => uint) public cleanClaims;
    mapping(address => uint) public advClaims;

    bytes16 totalCleanPool;
    bytes16 totalAdvPool;
    address payable public thirdPartyAddress;
    uint start;
    uint end;
    address payable seller;
    uint public price;
    uint testerShare;
    uint public testPool;
    uint startTime;
    uint public ownerDeposit;
    uint cleanDeposit;
    uint adversarialDeposit;
    uint public cleanCount;
    uint public advCount;
    uint public buyerIndex;
    uint possibleClients;
    bytes16 priceBytes16;
    bytes16 decay;
    uint hundred;
    bytes16 hundred16;
    int negOne;
    bytes16 negOne16;
    bytes16 possibleClients16;
    bytes16 formulaDenominator;
    bool collateralWasPaid;
    uint coveredDeposits;
    bytes16 testerShare16;
    bool thirdPartyInvoked;
    bool forcedThirdInvocation;


    event ContractCreation(uint _price, uint _possibleClients, uint _decayPct, uint _durationInDays, uint _testerShare, address sellerAddress);
    /*
    Constructor of the contract with the following arguments:
    _price : the price of the dataset
    posClients : the expected amount of people that will buy the dataset (affects seller's deposit decay)
    _decaypct : variable that affects the deposit decay (in percentages)
    _durationInDays : period of time in days when the people can buy the dataset and submit claims
    */
    constructor(uint _price, uint _possibleClients, uint _decayPct, uint _durationInDays, uint _testerShare, address payable _thirdPartyAddress) public {
        hundred = 100;
        hundred16 = hundred.fromUInt();
        negOne = - 1;
        negOne16 = negOne.fromInt();
        seller = msg.sender;
        startTime = now;
        price = _price;
        possibleClients = _possibleClients;
        testerShare = _testerShare;
        possibleClients16 = possibleClients.fromUInt();
        priceBytes16 = price.fromUInt();
        decay = _decayPct.fromUInt();
        decay = decay.div(hundred16);
        testerShare16 = (testerShare.fromUInt()).div(hundred16);
        formulaDenominator = decay.mul(possibleClients16.mul(negOne16));
        start = now;
        end = now + (_durationInDays * 1 days);
        collateralWasPaid = false;

        coveredDeposits = 0;
        thirdPartyInvoked = false;
        forcedThirdInvocation = false;

        emit ContractCreation(_price, _possibleClients, _decayPct, _durationInDays, _testerShare, seller);
        thirdPartyAddress = _thirdPartyAddress;
    }


    /*
    Helper function that calculates the amount of wei/eth that the seller must
    deposit for the buyer with index "index"
    */
    function calcDepositByIndex(uint _index) public view returns (bytes16) {
        bytes16 index16 = _index.fromUInt();
        bytes16 fraction = index16.div(formulaDenominator);
        bytes16 multiplier = fraction.exp();
        return priceBytes16.mul(multiplier);
    }

    /*
    View function that returns the total amount the seller must deposit for him to
    be "in good standing"
    */
    function calculateSellerDeposit() public view returns (uint) {
        bytes16 neededDeposit;
        for (uint index = coveredDeposits; index < buyerIndex; index++) {
            neededDeposit = neededDeposit.add(calcDepositByIndex(index));
        }
        return neededDeposit.toUInt();
    }

    event SellerDeposit(address depAddress, uint depositedValue, uint valueForTestPool);
    event BuyerDeposit(address depAddress, uint depositedValue, uint valueForTestPool, uint IndexOfBuyer);

    /*
    Unique deposit function that takes in both the deposit of the seller and of the buyers
    */
    function deposit() public payable {
        require(now < end - 1 days);
        if (seller == msg.sender && buyerIndex > 0) {
            uint value = calculateSellerDeposit();
            require(msg.value == value);
            //uint amountToBeDeposited = msg.value * (100 - testerShare) / 100;
            uint amountToBeDeposited = msg.value.fromUInt().mul(hundred16.sub(testerShare.fromUInt()).div(hundred16)).toUInt();
            ownerDeposit += amountToBeDeposited;
            testPool += (msg.value - amountToBeDeposited);
            coveredDeposits = buyerIndex;
            collateralWasPaid = true;
            emit SellerDeposit(msg.sender, amountToBeDeposited, msg.value - amountToBeDeposited);
        } else {
            buyersArray.push(msg.sender);
            buyers[msg.sender] = 1;
            buyerIndex++;
            collateralWasPaid = false;
            emit BuyerDeposit(msg.sender, msg.value, msg.value, buyerIndex);
        }
    }

    /*
    View function that returns what amount one can bet on an adversarial claim at
    a given time
    */
    function getAdversarialClaimCost() public view returns (uint) {
        return (calcDepositByIndex(advClaimantArray.length).mul(testerShare.fromUInt()).div(hundred16)).toUInt();
    }

    /*
    View function that returns what amount one can bet on an adversarial claim at
    a given time
    */
    function getCleanClaimCost() public view returns (uint) {
        return (calcDepositByIndex(cleanClaimantArray.length).mul(testerShare.fromUInt()).div(hundred16)).toUInt();
    }


    event AdversarialClaim(address claimantAddress, string advMethod, uint claimNumber);
    /*
    Function that submits a claim that the dataset contains adversarial images altered
    using the technique included in the parameter "advMethod"
    */
    function claimAdversarial(string memory _advMethod) public payable {
        require(buyers[msg.sender] == 1 && cleanClaims[msg.sender] == 0 && advClaims[msg.sender] == 0);
        bytes16 requiredAmount16 = calcDepositByIndex(advClaimantArray.length).mul(testerShare.fromUInt()).div(hundred16);
        require(requiredAmount16.toUInt() == msg.value);
        advClaimant memory claimant;
        claimant.adversarialGenMethod = _advMethod;
        claimant.claimAddress = msg.sender;
        claimant.sizeOfBet = msg.value;
        advClaimantArray.push(claimant);
        advClaims[msg.sender] = advClaimantArray.length;
        advCount++;
        totalAdvPool = totalAdvPool.add(requiredAmount16);
        emit AdversarialClaim(msg.sender, _advMethod, advCount);

    }

    event CleanClaim(address claimantAddress, uint claimNumber);
    /*
    Function that submits a claim that the dataset doesnt contain adversarial images
    */
    function claimClean() public payable {
        require(buyers[msg.sender] == 1 && cleanClaims[msg.sender] == 0 && advClaims[msg.sender] == 0);
        bytes16 requiredAmount16 = calcDepositByIndex(cleanClaimantArray.length).mul(testerShare.fromUInt()).div(hundred16);
        require(requiredAmount16.toUInt() == msg.value);
        cleanClaimant memory claimant;
        claimant.claimAddress = msg.sender;
        claimant.sizeOfBet = msg.value;
        cleanClaimantArray.push(claimant);
        cleanClaims[msg.sender] = cleanClaimantArray.length;
        cleanCount++;
        totalCleanPool = totalCleanPool.add(requiredAmount16);
        emit CleanClaim(msg.sender, cleanCount);
    }

    /*
    Function that returns the amount required in order for a cleanClamant to be transfered
    to the adversarialClaimants pool
    */
    function calcTransferCost() public view returns (uint) {
        require(cleanClaims[msg.sender] > 0);
        if (cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet > getAdversarialClaimCost()) {
            return 0;
        } else {
            return getAdversarialClaimCost() - cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet;
        }
    }

    event TransferToAdversarial(address transferAddress);
    //Can be refactored
    function transferToAdv(string memory _advMethod) public payable {
        require(now < end - 1 days);
        require(cleanClaims[msg.sender] > 0);
        //TODO remove comment
        require(now < end - 1 days);
        if (calcTransferCost() == 0) {

            uint value = getAdversarialClaimCost();
            advClaimant memory claimant;
            msg.sender.transfer(cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet - value);
            totalCleanPool = totalCleanPool.sub(cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet.fromUInt());
            totalAdvPool = totalAdvPool.add(value.fromUInt());
            claimant.adversarialGenMethod = _advMethod;
            claimant.claimAddress = msg.sender;
            claimant.sizeOfBet = value;
            advClaimantArray.push(claimant);
            advClaims[msg.sender] = advClaimantArray.length;
            delete cleanClaimantArray[cleanClaims[msg.sender] - 1];
            cleanClaims[msg.sender] = 0;

        } else {
            uint transferCost = calcTransferCost();
            require(msg.value == transferCost);

            advClaimant memory claimant;
            claimant.adversarialGenMethod = _advMethod;
            claimant.sizeOfBet = cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet + transferCost;
            claimant.claimAddress = msg.sender;
            totalCleanPool = totalCleanPool.sub(cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet.fromUInt());
            totalAdvPool = totalAdvPool.add((cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet + transferCost).fromUInt());
            delete cleanClaimantArray[cleanClaims[msg.sender] - 1];
            cleanClaims[msg.sender] = 0;
        }
        cleanCount--;
        advCount++;
        emit TransferToAdversarial(msg.sender);
    }

    /*
    Getter function for the seller's address
    */
    function getSellerAddress() public view returns (address) {
        return seller;
    }

    function getCurrentDatasetOpinion() public view returns (int) {
        //   require(now > (end - 1 days));
        //divison by zero checks
        uint cleanCountForRatio = 1;
        if (cleanCount > cleanCountForRatio)
            cleanCountForRatio = cleanCount;
        uint advCountForRatio = 1;
        if (advCount > advCountForRatio)
            advCountForRatio = advCount;
        //Case when dataset was deemed cleen by testers
        if (cleanCountForRatio / advCountForRatio >= 2) {
            return 1;
        } else if (advCountForRatio / cleanCountForRatio >= 2) {
            return - 1;
        } else {
            return 0;
        }
    }

    event ClaimantWithdrawal(address claimAddress, uint amountWithdrawn);
    event SellerWithdrawal(address sellerAddress, uint amountWithdrawn);
    event ThirdPartyInvocation(address invokerAddress);
    event BuyerRefund(address buyerAddress);

    /*
    Function which when called by the seller/one of the buyers rewards him with the correct amount
    depending on whether the dataset was adversarial or not or if a thirdParty verification
    engine was used
    */
    function getReward() public payable {
        //require(now > end); //REMOVE THIS BEFORE DEPLOYMENT
        require(thirdPartyInvoked == false);
        require(forcedThirdInvocation == false);
        //Case when dataset was deemed cleen by testers
        if (collateralWasPaid == true) {
            if (getCurrentDatasetOpinion() == 1) {
                if (msg.sender == seller) {
                    //                require(collateralWasPaid == true);
                    uint transferValue = ownerDeposit + (buyerIndex * price);
                    seller.transfer(ownerDeposit + (buyerIndex * price));
                    emit SellerWithdrawal(msg.sender, transferValue);
                    return;
                } else {
                    require(cleanClaims[msg.sender] > 0);
                    uint betSize = cleanClaimantArray[cleanClaims[msg.sender] - 1].sizeOfBet;
                    uint transferValue = (betSize.fromUInt().div(totalCleanPool).mul(testPool.fromUInt().add(totalAdvPool))).toUInt() + betSize;
                    msg.sender.transfer(transferValue);
                    emit ClaimantWithdrawal(msg.sender, transferValue);
                    cleanClaims[msg.sender] = 0;
                    return;

                }

            } else if (getCurrentDatasetOpinion() == - 1) {
                require(buyers[msg.sender] == 1);

                msg.sender.transfer(price);
                emit BuyerRefund(msg.sender);
                if (advClaims[msg.sender] > 0) {
                    uint betSize = advClaimantArray[advClaims[msg.sender] - 1].sizeOfBet;
                    uint transferValue = betSize.fromUInt().div(totalAdvPool).mul((testPool.fromUInt().add(ownerDeposit.fromUInt().add(totalCleanPool)))).toUInt() + betSize;
                    msg.sender.transfer(transferValue);
                    emit ClaimantWithdrawal(msg.sender, transferValue);

                }

                buyers[msg.sender] = 0;

            } else {
                thirdPartyInvoked = true;
                emit ThirdPartyInvocation(msg.sender);

            }
        }
        else {
            require(buyers[msg.sender] == 1);
            msg.sender.transfer(price);
            emit BuyerRefund(msg.sender);
            if (advClaims[msg.sender] > 0) {
                uint betSize = advClaimantArray[advClaims[msg.sender] - 1].sizeOfBet;
                uint transferValue = betSize.fromUInt().div(totalAdvPool).mul((testPool.fromUInt().add(ownerDeposit.fromUInt().add(totalCleanPool)))).toUInt() + betSize;
                msg.sender.transfer(transferValue);
                emit ClaimantWithdrawal(msg.sender, transferValue);
            }
            buyers[msg.sender] = 0;

        }
    }

    event ThirdPartyDecision(address thirdPartyAddress, int decision);
    event ThirdPartyPayment(address thirdPartyAddress, uint amountWithdrawn);
    //1 = clean, -1 = adversarial, anything else rejects
    function thirdPartyDecision(int _decision) public payable {
        require(thirdPartyInvoked = true && msg.sender == thirdPartyAddress);
        if (_decision == 1) {

            seller.transfer(ownerDeposit + (buyerIndex * price));

            emit SellerWithdrawal(seller, ownerDeposit + (buyerIndex * price));
            for (uint i = 0; i < cleanClaimantArray.length; i++) {
                uint claimReward = cleanClaimantArray[i].sizeOfBet.fromUInt().div(totalCleanPool).mul(testPool.fromUInt()).toUInt() + cleanClaimantArray[i].sizeOfBet;
                cleanClaimantArray[i].claimAddress.transfer(claimReward);
                emit ClaimantWithdrawal(cleanClaimantArray[i].claimAddress, claimReward);
            }
            msg.sender.transfer(totalAdvPool.toUInt());
            emit ThirdPartyPayment(msg.sender, totalAdvPool.toUInt());
            emit ThirdPartyDecision(msg.sender, 1);
        } else if (_decision == - 1) {

            for (uint i = 0; i < buyerIndex; i++) {
                msg.sender.transfer(price);
                emit BuyerRefund(buyersArray[i]);
            }

            for (uint i = 0; i < cleanClaimantArray.length; i++) {
                uint claimReward = advClaimantArray[i].sizeOfBet.fromUInt().div(totalAdvPool).mul(testPool.fromUInt().add(ownerDeposit.fromUInt())).toUInt() + advClaimantArray[i].sizeOfBet;
                advClaimantArray[i].claimAddress.transfer(claimReward);
                emit ClaimantWithdrawal(advClaimantArray[i].claimAddress, claimReward);

            }
            msg.sender.transfer(totalCleanPool.toUInt());
            emit ThirdPartyPayment(msg.sender, totalCleanPool.toUInt());
            emit ThirdPartyDecision(msg.sender, - 1);
        }

    }

    function getForcedInvocationCost() public view returns (uint){
        return totalAdvPool.toUInt();
    }


    function invokeThirdParty() public payable {
        //Remove comment below before deployment
        require(/*now > end - 1 days && now < end &&*/ msg.value == totalAdvPool.toUInt() && msg.sender == seller);
        forcedThirdInvocation = true;
        emit ThirdPartyInvocation(msg.sender);
    }

    event ForcedThirdPartyDecision(address thirdPartyAddress, uint cost, int decision);

    function forcedThirdPartyDecision(int _decision) public payable {
        require(thirdPartyInvoked = true && msg.sender == thirdPartyAddress);
        if (_decision == 1) {
            seller.transfer(ownerDeposit + (buyerIndex * price) + totalAdvPool.toUInt());
            emit SellerWithdrawal(seller, ownerDeposit + (buyerIndex * price));
            if (cleanClaimantArray.length > 0) {
                for (uint i = 0; i < cleanClaimantArray.length; i++) {
                    uint claimReward = cleanClaimantArray[i].sizeOfBet.fromUInt().div(totalCleanPool).mul(testPool.fromUInt()).toUInt() + cleanClaimantArray[i].sizeOfBet;
                    cleanClaimantArray[i].claimAddress.transfer(claimReward);
                    emit ClaimantWithdrawal(cleanClaimantArray[i].claimAddress, claimReward);

                }
            }
            else {
                seller.transfer(testPool);
            }
            msg.sender.transfer(address(this).balance);
            emit ForcedThirdPartyDecision(msg.sender, totalAdvPool.toUInt(), _decision);
        } else if (_decision == - 1) {
            for (uint i = 0; i < buyerIndex; i++) {
                msg.sender.transfer(price);
                emit BuyerRefund(buyersArray[i]);
            }
            for (uint i = 0; i < advClaimantArray.length; i++) {
                uint claimReward = advClaimantArray[i].sizeOfBet.fromUInt().div(totalAdvPool).mul(testPool.fromUInt().add(ownerDeposit.fromUInt().add(totalCleanPool))).toUInt() + advClaimantArray[i].sizeOfBet;
                advClaimantArray[i].claimAddress.transfer(claimReward);
                emit ClaimantWithdrawal(advClaimantArray[i].claimAddress, claimReward);
            }
            msg.sender.transfer(totalAdvPool.toUInt());
            emit ForcedThirdPartyDecision(msg.sender, totalAdvPool.toUInt(), _decision);
        }

    }

    /*
    Default fallback function
    */
    function() external payable {
        deposit();
    }

    //   helper functions for debugging/development
    function incrementValues() public payable {
        advClaimant memory adv;
        advClaimantArray.push(adv);
    }

    function getArrayLength() public view returns (uint) {
        return advClaimantArray.length;
    }

    function getAdvClaimStrings(uint _index) public view returns (string memory) {
        return advClaimantArray[_index].adversarialGenMethod;
    }

    function getContractBalance() public view returns (uint) {
        return address(this).balance;
    }

    function getContractAddress() public view returns (address) {
        return address(this);
    }

}