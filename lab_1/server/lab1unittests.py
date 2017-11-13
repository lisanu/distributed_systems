__author__ = 'cylic'

from urllib2 import HTTPError
import urllib
import urllib2
import sys
import unittest
from random import randint
from time import sleep

def page_contents(page, message, method='GET'):
    if 'POST' in method:
        data = urllib.urlencode(message)
        request = urllib2.Request(page, data)
        request.get_method = lambda : 'POST'
    else:
        request = urllib2.Request(page)
    return urllib2.urlopen(request)

class TestBlackBoardLab1(unittest.TestCase):
    "Tests for EDA 592 (Distributed Systems) Assignment 1"

    def __init__(self, testname, number_of_vessels):
        super(TestBlackBoardLab1, self).__init__(testname)
        self.number_of_vessels = number_of_vessels


    def test_delete(self):
        #make sure that "hello 4" message exists
        self.test_add()

        # hello 4
        # random vessel
            # delete it from random vessel
        # check that it does not exist in any of the vessels


    def test_update(self):
        # ??? what if it already exists??

        #add hello 4
        self.test_add()

        # random vessel
            # update it from random vessel

        # check that all are updated

    def test_consistency(self):
        pass

    def message_not_exists_in(self, message, vessel_list):
        #check that no vessel contains our message; since our system may be inconsistent
        for i in vessel_list:
            #create an address
            address = "http://10.1.0." + str(i) + "/board"
            #check a page doesn't contain a message
            original_content = page_contents(address, "")
            temp = original_content.read()
            #make sure that message doenot exist in the board
            self.assertFalse(message in temp, "Message was already in the board! delete it rerun the test")


    def test_add(self):
        message = "hello 4"
        #check that no vessel contains our message; since our system may be inconsistent
        for i in range(1,number_of_vessels):
            #create an address
            address = "http://10.1.0." + str(i) + "/board"
            #check a page doesn't contain a message
            original_content = page_contents(address, "")
            temp = original_content.read()
            #make sure that message doenot exist in the board
            self.assertFalse(message in temp, "Message was already in the board! delete it rerun the test")

        #pick a random server for posting
        server_address = "http://10.1.0." + str(randint(1, number_of_vessels)) + "/board"
        post_message = {}
        post_message['entry'] = message

        try:
            page_contents(server_address, post_message, 'POST')
        except HTTPError as e:
            self.assertFalse(False)

        sleep(8)

        #check that no vessel contains our message; since our system may be inconsistent
        for i in range(1, number_of_vessels):
            #create an address
            address = "http://10.1.0." + str(i) + "/board"
            #check a page doesn't contain a message
            response = page_contents(address, "")
            content = response.read()
            #make sure that message doenot exist in the board
            self.assertTrue(message in content, "Message not found in vessel 10.1.0." + str(i))

if __name__ == '__main__':
    # Checking the arguments
    if len(sys.argv) != 2:
        print("Arguments: Specify the number_of_vessels")

    else:
        number_of_vessels = int(sys.argv[1])
        test_loader = unittest.TestLoader()
        test_names = test_loader.getTestCaseNames(TestBlackBoardLab1)

        suite = unittest.TestSuite()
        for test_name in test_names:
            suite.addTest(TestBlackBoardLab1(test_name, number_of_vessels))

        result = unittest.TextTestRunner().run(suite)
        sys.exit(not result.wasSuccessful())
