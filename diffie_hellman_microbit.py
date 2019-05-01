# Diffie-Hellman Key Exchange over micro:bit
# Author: Owen Brasier, Australian Comptuing Academy, 2019
# Licence: MIT
# INSTRUCTIONS:
# You will need 2 micro:bits loaded with this program. On each, set the following variables:
# ME, RECEIVER, text
# to be your name, who you are sending the message to, and what the message is
# Pick a number for the secret key in MY_SECRET_KEY, don't tell anyone this key

# To operate the program:
# Press A to perform a key exchange (only one of you needs to press this)
# Press B to send the message. The receiver will scroll the message and print it to the console.

# These variables must be the same across both micro:bits:
# Make sure SHARED_PRIME and SHARED_BASE are the same across both micro:bits
# The SHARED_PRIME can be any prime, the SHARED_BASE is a primitive root modulo
# You can add a router from module 3 between these devices to forward these messages.

from microbit import *
import radio

# CHANGE THESE:
# who you are, who you are sending a message to, and the plaintext message to send
ME = 'Alice'
RECEIVER = 'Bob'
# does not support accented characters
TEXT = 'secret message'
# your secret key, set this and don't tell anyone, this must be kept private
MY_SECRET_KEY = 6

# DON'T CHANGE THESE (or keep them the same for both micro:bits):
# please note, real encryption uses numbers that are MUCH larger than these
# shared prime number, known as n, this must be the same for both, can be public
SHARED_PRIME = 541
# shared base, known as g, this must be the same for both, can be public
SHARED_BASE = 10

# image strings, for a key and a locked/unlocked symbol
KEY = '00000:09000:90999:09009:00000'
UNLOCKED = '00900:09090:09000:09990:09990'
LOCKED = '00900:09090:09090:09990:09990'

# This is the calculated key that we can send publicly to perform the key exchange
CALCULATED_KEY = (SHARED_BASE**MY_SECRET_KEY) % SHARED_PRIME

def create_message(destination, payload):
  '''Create a message to be send to the destination.'''
  return '{}:{}:{}'.format(ME, destination, payload)

def get_diffie_hellman_shared_secret(partner_calculated_key):
  '''Calculate the diffie hellman shared secret.'''
  return (partner_calculated_key ** MY_SECRET_KEY) % SHARED_PRIME

def rotate(letter, key):
  '''Rotate a lower or uppercase letter by key.'''
  if letter.islower():
    code = (ord(letter) - ord('a') + key) % 26 + ord('a')
    return chr(code)
  elif letter.isupper():
    code = (ord(letter) - ord('A') + key) % 26 + ord('A')
    return chr(code)
  return letter

def encrypt(plaintext, key):
  '''Take a message it and encrypt it using a caeser cipher.'''
  ciphertext = ''
  for letter in plaintext:
    ciphertext += rotate(letter, key)
  return ciphertext

def decrypt(ciphertext, key):
  '''Decrypt the message.'''
  return encrypt(ciphertext, -key)

def show_and_sleep(image, delay):
  '''Show an image for delay milliseconds.'''
  display.show(image)
  sleep(delay)
  display.clear()

# make sure you are both on the same channel, unless you have a router micro:bit
radio.config(channel=8)
radio.on()

# if our connection is encrypted
encrypted = False
# if we have sent our calculated public key
key_sent = False
while True:
  # Handle incoming message
  msg = radio.receive()
  if msg:
    source, destination, payload = msg.split(':')
    if destination == ME:
      # if we haven't performed key exchange yet, do so, this must always be the first message
      if not encrypted:
        shared_secret = get_diffie_hellman_shared_secret(int(payload))
        # take the mod 26 of the shared_secret - this will be the amount we rotate the text
        # in our caeser cipher
        offset = shared_secret % 26
        encrypted = True
        if not key_sent:
          message = create_message(RECEIVER, CALCULATED_KEY)
          radio.send(message)
          key_sent = True
        show_and_sleep(Image(KEY), 2000)
      # we have performed key exchange, so decrypt the message and print/scroll it
      else:
        decrypted = decrypt(payload, offset)
        print('encrypted:', payload, 'decrypted:', decrypted)
        display.scroll(decrypted)
  # Press button A to perform the key exchange.
  if button_a.was_pressed():
    message = create_message(RECEIVER, CALCULATED_KEY)
    radio.send(message)
    key_sent = True
    display.show(Image(KEY))
  # Press button B to send the encrypted message
  if button_b.was_pressed() and encrypted:
    encrypted_text = encrypt(TEXT, offset)
    message = create_message(RECEIVER, encrypted_text)
    radio.send(message)
    show_and_sleep(Image.ARROW_E, 1000)
  # show locked symbol if we're ready to communicate
  if encrypted:
    display.show(Image(LOCKED))
  else:
    display.show(Image(UNLOCKED))
