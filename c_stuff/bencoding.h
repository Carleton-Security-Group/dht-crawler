#ifndef BENCODING_H
#define BENCODING_H 1

struct bstr *bencode(struct value *value);

struct value *bdecode(struct bstr *b);

#endif
