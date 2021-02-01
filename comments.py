# lists commentaries in CSV format from specified topic and group in VK:
# datetime, author, commentary

import requests
from datetime import datetime
from configparser import ConfigParser
from os.path import expanduser
import vk_api
import re
import csv
import sys
import argparse

# VK credentials must be specified in INI file ~/.vk/credentials:
#
# [default]
# vk_login = xxxxx
# vk_password = xxxxx

def userinfo(user_id):
  
  # returns String "user first<space>last name"
  # calls vk API if user ID not found in user_dict  
  # uses/updates global user_dict

  if user_id not in user_dict:
    user = vk.users.get(user_ids=user_id)
    user_dict[user_id] = { 'first_name': user[0]["first_name"], 'last_name': user[0]["last_name"] }

  return user_dict[user_id]["first_name"] + " " + user_dict[user_id]["last_name"]

def msg_datetime(timest):

  # returns vk comment create date human readable string 
  str = datetime.fromtimestamp(timest).strftime("%d-%m-%Y %H:%M:%S")
  return str

def msg_text(txt):

  # returns cleaned comment text (remove special markup at beginning) 
  str = re.sub('\[.*\],', '', txt)
  return str

def creds(creds_file=expanduser("~")+'/.vk/credentials'):

  config = ConfigParser()
  config.read(creds_file)

  return ( config.get('default', 'vk_login'), config.get('default', 'vk_password') )

#=== functions end

# Argument parser
parser = argparse.ArgumentParser(usage='%(prog)s --group_id=<Num> --topic_id=<Num>')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-g', '--group_id', type=int, help='VK group id', required=True)
requiredNamed.add_argument('-t', '--topic_id', type=int, help='VK topic id', required=True)

args = parser.parse_args()

group_id = args.group_id
topic_id = args.topic_id

# user ids and names
user_dict = {}

login, password = creds()
vk_session = vk_api.VkApi(login, password)

try:
  vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
  print(error_msg)
  exit

vk = vk_session.get_api()
comments = vk.board.getComments(group_id=group_id, topic_id=topic_id, count=100, extended=1)

if comments['items']:
  
  # prepare cvs file/output
  writer = csv.writer(sys.stdout, delimiter=',')

  # sort messages by create date (unix timestamp)
  for msg in comments['items']:

  	# negative from_id are reserved for vk system internal users such as group author
  	# we use only real users
    if msg["from_id"] > 0:

      # output CVS line
      writer.writerow([ msg_datetime(msg["date"]), userinfo(msg["from_id"]), msg_text(msg["text"]) ])
