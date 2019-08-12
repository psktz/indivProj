from brownie import *
import time


"""
Scenario description:
- dataset is priced at 100000000000000000000 wei.
- the seller believes there will be around 100 buyers
- the decay percentage rate (the coefficient between 0 and 1 in the formula) is 50
- contract duration equal to 30 days
- tester share is equal to 20 percentage points

Flow of actions:
1. Seller deploys contract
2. Ten people buy the dataset
3. The first five buyers claim the dataset is clean
4. The sixth buyer claims the dataset is adversarial
5. The fifth buyer switches his claim from clean to adversarial 
6. The seller pays all the necessary deposit on his side
7. Contract passes the required duration of 30 days and is deemed clean
8. The seller withdraws his share from the contract balance
9. All the clean claimants withdraw their share from the contract balance 
"""


"""
Helper function used to print the ballance of all the accounts
"""
def printAccountValues():
    for i in range(11):
        print("Account number " + str(i)+ " has balance " + str(a[i].balance()))

def main():
    print("1. Seller deploys contract")
    t = accounts[0].deploy(PrototypeContract, 100000000000000000000, 100, 50, 30, 20,a[11])

    printAccountValues()

    print("#2. Ten people buy the dataset")
    for i in range(10):
        t.deposit({'from': accounts[i+1], 'value': 100000000000000000000})


    print("#3. The first five buyers claim the dataset is clean")
    for i in range(5):
        value = t.getCleanClaimCost()
        t.claimClean({'from': accounts[i+1], 'value': value})

    print("#4. The sixth buyer claims the dataset is adversarial")
    advValue = t.getAdversarialClaimCost()
    t.claimAdversarial("fgsm",{'from': accounts[6], 'value': advValue})

    printAccountValues()

    print("#5. The fifth buyer switches his claim from clean to adversarial")
    costOfTransfer = t.calcTransferCost({'from': accounts[5]})
    t.transferToAdv("fgsm-adv", {'from': accounts[5], 'value': costOfTransfer})

    print("#6. The seller pays all the necessary deposit on his side")
    neededSellerDeposit = t.calculateSellerDeposit()
    t.deposit({'from': a[0],'value': neededSellerDeposit})

    print("#7.Contract passes the required duration of 30 days and is deemed clean")

    print("#8. The seller withdraws his share from the contract balance")
    t.getReward({'from':a[0]})

    printAccountValues()

    print("#9. All the clean claimants withdraw their share from the contract balance")
    for i in range(4):
        t.getReward({'from':a[i+1]})

    printAccountValues()

    print("The amount of wei remaining in the contract after the scenario execution: "+str(t.getContractBalance()))
if __name__ == "__main__":
    main()
