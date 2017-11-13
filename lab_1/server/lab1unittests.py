__author__ = 'cylic'

from urllib2 import HTTPError
import urllib
import urllib2
import sys
import unittest
from random import randint
from time import sleep
import re

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
        original_message = "hello 4"

        # check the message we want to test deleting exists, add it if it doesn't call test_add and add it!
        # exists[0] indicates if message exists, exists_in[1] stores the contents of the board if original_message
        # exists in the board
        exists_in = self.message_exists_in(original_message, range(1, self.number_of_vessels))
        if not exists_in[0]:
            self.test_add()

        #check that the message exists again! It should exist now!
        exists_in = self.message_exists_in("hello 4", range(1, self.number_of_vessels))
        self.assertTrue(exists_in[0], "Message could not be added! Check your add logic")

        #extract the id of message from the returned board contents
        id_to_modify = self.get_id_of_message(original_message, exists_in[1])

        # pick up a random vessel and update the message!
        server_address = "http://10.1.0." + str(randint(1, number_of_vessels)) + "/entries/" + id_to_modify
        #construct data to be sent
        post_message = {}
        post_message['delete'] = 1
        post_message['entry'] = ""

        #send the data to the selected vessel
        try:
            page_contents(server_address, post_message, 'POST')
        except HTTPError as e:
            self.assertFalse(False)

        #wait for the delete operation to be to be propagated
        sleep(5)

        #check the deleted message exists does not exist in any of the vessels
        self.assertFalse(self.message_exists_in(original_message, range(1, 10), False)[0], "Message not deleted!")



    def test_update(self):
        original_message = "hello 4"
        new_message = original_message + " updated"

        # check the message we want to test updating exists, add it if it doesn't calling message_exists_in
        # exists[0] indicates if message exists, exists_in[1] stores the contents of the board where original_message
        # exists in
        exists_in = self.message_exists_in(original_message, range(1, self.number_of_vessels))
        if not exists_in[0]:
            self.test_add()

        #check that the message exists again! It should exist now!
        exists_in = self.message_exists_in("hello 4", range(1, self.number_of_vessels))
        self.assertTrue(exists_in[0], "Message could not be added!")

        #extract the id of message from the returned board contents
        id_to_modify = self.get_id_of_message(original_message, exists_in[1])

        # pick up a random vessel and update the message!
        server_address = "http://10.1.0." + str(randint(1, number_of_vessels)) + "/entries/" + id_to_modify
        #construct data to be sent
        post_message = {}
        post_message['delete'] = 0
        post_message['entry'] = new_message

        #send the data to the selected vessel
        try:
            page_contents(server_address, post_message, 'POST')
        except HTTPError as e:
            self.assertFalse(False)

        #wait for the message to be propagated
        sleep(5)

        #check the updated message exists in all vessels
        self.assertTrue(self.message_exists_in(new_message, range(1, 10))[0], "Message not updated!")

    def get_id_of_message(self, message, check_in):
        #get all forms
        forms = re.findall("<form(.*?)</form>", check_in, re.S)

        #find the single form that contains the
        enclosing_form = ""
        for form in forms:
            if '"'+ message + '"' in form:
                enclosing_form = form
                break

        #start and ending of the id
        start = enclosing_form.find("value=\"") + 7
        end = enclosing_form.find("\" readonly")

        # return the id of message in board_contents
        # Note if the system is inconsistent, this can return different values in different vessels
        return enclosing_form[start: end]

    def message_exists_in(self, message, vessel_list, check_all=True):
        temp = ""
        #check that no vessel contains our message; since our system may be inconsistent
        for i in vessel_list:
            #create an address
            address = "http://10.1.0." + str(i) + "/board"
            #check a page doesn't contain a message
            original_content = page_contents(address, "")
            temp = original_content.read()
            #make sure that message doenot exist in the board
            if check_all:
                if '"'+ message + '"' not in temp:
                    return False, ""
            else:
                if '"' + message + '"' in temp:
                    return True, temp
        if check_all:
            return True, temp
        else:
            return False, ""


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
            self.assertFalse(('"' + message + '"') in temp, "Message was already in the board! delete it rerun the test")

        #pick a random server for posting
        server_address = "http://10.1.0." + str(randint(1, number_of_vessels)) + "/board"
        post_message = {}
        post_message['entry'] = message

        try:
            page_contents(server_address, post_message, 'POST')
        except HTTPError as e:
            self.assertFalse(False)

        sleep(5)

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
