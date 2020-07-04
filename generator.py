#!/bin/env python3
# -*- coding: utf-8 -*-

# JS Vault generator
import json, argparse, math, os
import nacl.pwhash.argon2id, nacl.utils, nacl.secret
from mako.template import Template

parser = argparse.ArgumentParser(prog='jsvaultgen')
parser.add_argument('--input', dest='inspec', required=True, help='Input JSON file with questions and answers')
parser.add_argument('--content', dest='content', required=True, help='The contents of the safe')
parser.add_argument('--output', dest='out', required=True, help='Output HTML file')
args = parser.parse_args()

templ = Template(open("template.html", "r").read())
qspec = json.loads(open(args.inspec, "r").read())
content = open(args.content, "rb").read()

# Process input and calculate a few things
entropy = 0
for q in qspec["questions"]:
	if "entropy" in q:
		entropy += q["entropy"]
	elif q["t"] == "text":
		entropy += 4 * len(q["a"])
	elif q["t"] == "choice":
		entropy += math.log2(len(q["opts"]))
	elif q["t"] == "mchoice":
		entropy += len(q["opts"])

password = b""
for q in qspec["questions"]:
	if q["t"] == "text":
		password += q["a"].encode("utf-8") + b"\0"
	elif q["t"] == "choice":
		assert(len(q["opts"]) == len(set(q["opts"])))
		a = q["opts"][0]
		q["opts"] = sorted(q["opts"])
		password += b"%08d\0" % q["opts"].index(a)
	elif q["t"] == "mchoice":
		assert(len(q["opts"]) == len(set(q["opts"])))
		a = q["opts"][:q["validcnt"]]
		q["opts"] = sorted(q["opts"])
		password += b"".join(b"1" if x in a else b"0" for x in q["opts"]) + b"\0"

print("Approximate entropy %0.02f bits" % entropy)
if entropy < 256:
	print("WARNING! We recommend using an entropy of at least 256 bits")
elif entropy < 128:
	print("WARNING! Using an entropy lower than 128 bits is dangerous!")

# Proceed to seal the content
password_salt = nacl.utils.random(nacl.pwhash.argon2id.SALTBYTES)
password_hash = nacl.pwhash.argon2id.kdf(128, password, password_salt, nacl.pwhash.argon2id.OPSLIMIT_INTERACTIVE, 2*1024*1024)

content_nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
encrypter = nacl.secret.SecretBox(password_hash[:nacl.secret.SecretBox.KEY_SIZE])
sealed_content = encrypter.encrypt(content, nonce=content_nonce).ciphertext  # Includes the HMAC


def b2a(b):
	return "new Uint8Array([%s])" % (",".join(str(x) for x in b))

open(args.out, "w").write(templ.render(
	questions = qspec["questions"], note = qspec["note"],
	content_filename = os.path.basename(args.content),
	sealed_content = b2a(sealed_content),
	content_nonce = b2a(content_nonce),
	password_salt = b2a(password_salt)))


