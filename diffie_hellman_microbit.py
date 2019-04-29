# Diffie-Hellman Key Exchange over micro:bit
# Author: Owen Brasier, Australian Comptuing Academy, 2019
# Licence: MIT
# INSTRUCTIONS:
# Pick a secret key in MY_SECRET_KEY, don't tell anyone this key
# Make sure SHARED_PRIME and SHARED_BASE are the same across both micro:bits
# The SHARED_PRIME can be any prime, the SHARED_BASE is a primitive root modulo 
# change the text variable to change the message to send.
# change the me variable to be your name
# change the receiver variable to be your friends name
# Press A to perform a key exchange (only one of you needs to press this)
# Press B to send the message. It will scroll the message and print it to the serial console.

from microbit import *
import radio

# your secret key, set this and don't tell anyone, this must be kept private
MY_SECRET_KEY = 6
# shared prime, known as n, this must be the same for both, can be public
SHARED_PRIME = 541
# shared base, known as g, this must be the same for both, can be public
SHARED_BASE = 10

# image strings, for a key and unlocked symbol
KEY = '00000:09000:90999:09009:0000'
UNLOCKED = '00900:09090:09000:09990:09990'
LOCKED = '00900:09090:09090:09990:09990'

# who you are, who you are sending a message to, and the plaintext message to send
# please change these
me = 'Alice'
receiver = 'Bob'
text = 'secret message'

# This is the calculated key that we can send publicly to perform the key exchange
calculated_key = (SHARED_BASE**MY_SECRET_KEY) % SHARED_PRIME

def create_message(destination, payload):
  '''Create a message to be send to the destination.'''
  return '{}:{}:{}'.format(me, destination, payload)

def get_diffie_hellman_shared_secret(sender_key):
  '''Calculate the diffie hellman shared secret.'''
  return (sender_key ** MY_SECRET_KEY) % SHARED_PRIME

def rotate(letter, key):
  '''Rotate a lower or uppercase letter by key.'''
  if letter.islower():
    code = (ord(letter) - ord('a') + key) % 26
    code += ord('a')
    return chr(code)
  elif letter.isupper():
    code = (ord(letter) - ord('A') + key) % 26
    code += ord('A')
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
    if destination == me:
      # if we haven't performed key exchange yet, do so, this must always be the first message
      if not encrypted:
        shared_secret = get_diffie_hellman_shared_secret(int(payload))
        offset = shared_secret % 26
        encrypted = True
        if not key_sent:
          message = create_message(receiver, calculated_key)
          radio.send(message)
          key_sent = True
        show_and_sleep(Image(KEY), 2000)
      # we have performed key exchange, so decrypt the message and print/scroll it
      else:
        decrypted = decrypt(payload, offset)
        print(payload, decrypted)
        display.scroll(decrypted)
  # Press button A to perform the key exchange.
  if button_a.was_pressed():
    message = create_message(receiver, calculated_key)
    radio.send(message)
    key_sent = True
    display.show(Image(KEY))
  # Press button B to send the encrypted message
  if button_b.was_pressed() and encrypted:
    encrypted_text = encrypt(text, offset)
    message = create_message(receiver, encrypted_text)
    radio.send(message)
    show_and_sleep(Image.ARROW_E, 1000)
  # show locked symbol if we're ready to communicate
  if encrypted:
    display.show(Image(LOCKED))
  else:
    display.show(Image(UNLOCKED))
