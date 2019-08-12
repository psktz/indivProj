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
3. The first four buyers claim the dataset is clean
4. The next four buyers claim the dataset is adversarial 
5. The seller pays all the necessary deposit on his side
6. Contract passes the required duration of 30 days and is deemed clean
7. Either the seller or a buyer triggers the third party
7. Third party deems the dataset clean
8. All the clean claimants withdraw their share from the contract balance 
"""

"""
Helper function used to print the ballance of all the accounts
"""


def printAccountValues():
    for i in range(11):
        print("Account number " + str(i) + " has balance " + str(a[i].balance()))


def main():
    print("1. Seller deploys contract")
    t = accounts[0].deploy(PrototypeOne, 100000000000000000000, 100, 50, 30, 20,a[11])

    printAccountValues()

    print("#2. Ten people buy the dataset")
    for i in range(10):
        t.deposit({'from': accounts[i + 1], 'value': 100000000000000000000})

    print("#3. The first four buyers claim the dataset is clean")
    for i in range(4):
        value = t.getCleanClaimCost()
        t.claimClean({'from': accounts[i + 1], 'value': value})

    print("#4. The next four buyers claim the dataset is adversarial")
    for i in range(4):
        advValue = t.getAdversarialClaimCost()
        t.claimAdversarial("fgsm", {'from': accounts[i + 5], 'value': advValue})

    printAccountValues()

    print("#5. The seller pays all the necessary deposit on his side")
    neededSellerDeposit = t.calculateSellerDeposit()
    t.deposit({'from': a[0], 'value': neededSellerDeposit})

    print("#6.Contract passes the required duration of 30 days")

    print("#7 Buyer triggers the third party")
    # print("#7. The seller withdraws his share from the contract balance")
    t.getReward({'from': a[1]})

    printAccountValues()

    print("#Third party declares dataset as clean and pays the rewards")
    t.thirdPartyDecision(1,{'from':a[11]})
    printAccountValues()

    print("The amount of wei remaining in the contract after the scenario execution: " + str(t.getContractBalance()))


if __name__ == "__main__":
    main()
