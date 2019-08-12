import pytest
import json
from brownie import *

value = 100000000000000000000

@pytest.fixture(scope="module", autouse=True)
def token(PrototypeOne, accounts):
    t = accounts[0].deploy(PrototypeOne, 100000000000000000000, 100, 50, 30, 20,accounts[11])
    yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    value = 100000000000000000000
    testPassed = False
    pass

def test_contractDeployment(token):
    assert token.price() == 100000000000000000000

def test_depositByBuyer(token):
    token.deposit({'from': accounts[1], 'value': value})
    token.deposit({'from': accounts[0], 'value': value})
    assert token.price() == value
    assert token.buyerIndex() == 1
    assert token.ownerDeposit() + token.testPool() == value

def test_depositByBuyerChangesCollateralBoolean(token):
    token.deposit({'from': accounts[1], 'value': value})
    assert token.collateralWasPaid() is False

def test_sellerCantDepositBeforeBuyer(token):
    testPassed = False
    try:
        token.deposit({'from':accounts[0],'value':value})
    except:
        testPassed = True
    assert testPassed == True

def test_DepositedAmountIsSplitWithTesters(token):
    token.deposit({'from': accounts[1],'value': value})
    token.deposit({'from': accounts[0],'value': value})
    assert token.ownerDeposit()+token.testPool() == value

def test_TheSameAddressCantBuyTheDatasetMoreThanOnce(token):
    testPassed = False
    token.deposit({'from': accounts[1],'value':value})
    try:
        token.deposit({'from': accounts[1], 'value': value})
    except:
        testPassed = True
    assert testPassed == True

def test_SellerCannotBuyDataset(token):
    testPassed = False
    token.deposit({'from': accounts[1],'value': value})
    token.deposit({'from': accounts[0],'value': value})
    try:
        token.deposit({'from': accounts[0], 'value': value})
    except:
        testPassed = True
    assert testPassed == True

def test_nonBuyersCannotMakeCleanClaims(token):
    testPassed = False
    token.deposit({'from': accounts[1], 'value': value})
    try:
        token.claimClean({'from':accounts[11],'value':value/5})
    except:
        testPassed = True
    assert testPassed == True

def test_nonBuyersCannotMakeAdversarialClaims(token):
    testPassed = False
    token.deposit({'from': accounts[1], 'value': value})
    try:
        token.claimAdversarial({'from':accounts[11],'value':value/5})
    except:
        testPassed = True
    assert testPassed == True

def test_sellerCannotMakeAdversarialClaims(token):
    testPassed = False
    try:
        token.claimAdversarial({'from':accounts[0],'value':value/5})
    except:
        testPassed = True
    assert testPassed == True


def test_sellerCannotMakeCleanClaims(token):
    testPassed = False
    try:
        token.claimClean({'from': accounts[0], 'value': value / 5})
    except:
        testPassed = True
    assert testPassed == True

def test_transferAdjustsTheNumberOfClaimantsOnEachSide(token):
    token.deposit({'from': accounts[1], 'value': value})
    token.deposit({'from': accounts[2], 'value': value})
    token.claimClean({'from': accounts[1], 'value': value / 5})
    token.claimAdversarial("fgsm",{'from': accounts[2], 'value': value / 5})
    cleanCountTest = token.cleanCount()
    advCountTest = token.advCount()
    token.transferToAdv("fgsm",{'from':accounts[1],'value':token.calcTransferCost({'from':accounts[1]})})
    assert cleanCountTest == token.cleanCount() + 1
    assert advCountTest == token.advCount() - 1

def test_datasetOpinionFunction(token):
    assert token.getCurrentDatasetOpinion() == 0
    token.deposit({'from': accounts[1], 'value': value})
    token.deposit({'from': accounts[2], 'value': value})
    token.claimClean({'from': accounts[1], 'value': token.getCleanClaimCost()})
    token.claimClean({'from': accounts[2], 'value': token.getCleanClaimCost()})
    assert token.getCurrentDatasetOpinion() == 1
    token.transferToAdv("fgsm", {'from': accounts[1], 'value': token.calcTransferCost({'from': accounts[1]})})
    token.transferToAdv("fgsm", {'from': accounts[2], 'value': token.calcTransferCost({'from': accounts[2]})})
    assert token.getCurrentDatasetOpinion() == -1