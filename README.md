
JS Vault
========

What's this?
------------

Do you want to store some secrets or sensible information that:

 - Is mostly static or seldmon updated
 - Can be easily accessed by non-technical users
 - Is securely stored
 - Can be accessed easily on every platform in an uncomplicated manner?

JS Vault is just that: a tool that produces an HTML file (with no dependencies,
so can be used offline) that has secrets embedded into it and can only be
accessed if the user knows a series of secrets (in the form of answers to
used defined questions).

How does it work?
-----------------

To create a vault you will need to write a JSON file with the questions and
answers. I plan to do an HTML user-friendly version of this at some point.

```json
{
  "note": "This is a simple note that can be used as instructions and remarks for the vault",
  "questions": [
    {
      "q": "What is my favourite icecream flavour",
      "t": "text",
      "a": "banana",
      "tip": "Write it lowercase",
      "entropy": 5
    },
    {
      "q": "What did I wear the first time we met?",
      "t": "choice",
      "opts": ["Jeans", "A pink hat", "Nothing at all"]
    },
    {
      "q": "Which movies have we watched toghether?",
      "t": "mchoice",
      "opts": ["Fast and Furious", "The Lord of the Rings", "Garfield", "Inception"],
      "validcnt": 2
    },
  ]
}
```

Every question has a text, stored in `q` and a type `t`. For text questions there's
an answer field `a` which the correct answer. You might also add a `tip` to any
question to give further guidance on how to answer the question (useful for text
questions since there could be confusion on accents or umlaut usage). For the
`choice` kind of question, the user has to choose one correct answer out of many.
The correct answer *must be* the first one in the list (don't worry they are always
alphabetically sorted). For `mchoice` the user has to select multiple answers
(this can be seen as N yes/no questions). The first options are the correct ones
as well, where `validcnt` indicates how many valid answers are.

In the example above the correct answers would be "banana", "Jeans" and
"Fast and Furious" + "The Lord of the Rings". The aproximate entropy of the
questionnare would be around 10.5 bits, since the first question has 5 bits
of entropy (cause we decided so, one could argue there's around ~30 flavours
of icecream, so 5 bits sounds reasonable) the second one has 1.5 bits and the
last one has 4 bits (one bit per option). By default text answers get 4 bits
of entropy per character, which is a rough aproximation.


How secure is this really?
--------------------------

Well like any security question it depends on how hard it is for people to
find out your answers. *Know your threat model* is my advice here.

You can use secret words, situations, memories and experiencies that only
you and the receiver know as long as they are hard to guess and there's
enough of them. So for example if the question has a small limited set
of answers (such as `which newspaper` or `what color`) the entropy will
be low and you will need to write many questions to get a decent amount of
entropy. That's of course assuming the answer cannot be discovered by other
means (like OSINT).

Aside from that, if the questions are solid, the security is provided by libNaCl
which is very secure. The password goes through a KDF based on Argon2, which
uses around 2MB of memory and requires a few CPU cycles to compute, slowing
down any bruteforce attempt. Furthermore in order to validate the password
the attacker needs to decrypt the data and then validate the HMAC which can be
extremely slow if the attached data is not small.


How does one unblock a secure document?
---------------------------------------

As simple as it sounds the user only needs to open the doc with a browser, fill
the form with the correct answers and press the button. A password will be
generated based on the responses and will be used to decrypt the payload. The
payload will be downloaded to the user as a regular file download. So it could
be a text file, a PDF, or whatever you want (as long as it's small-ish).

In order to conceal the document partially correct responses won't be revealed
to the user (as there's really no way of knowing) to avoid bruteforcing (well
to avoid efficient brute-forcing).


Dependencies
------------

This project uses libsodium for the crypto bits. The password is hashed with
some argon2 primitive and encrypted (+HMAC authentication). We use these two:

  - https://github.com/jedisct1/libsodium.js
  - https://github.com/pyca/pynacl

The contents are embedded in the HTML file, along with the CSS and JS files.

For the generator [mako](https://www.makotemplates.org/) is used as a template
engine to generate HTML output.


