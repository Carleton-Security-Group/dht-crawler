#ifndef BENCODING_H
#define BENCODING_H 1

struct bstr {
    char *s;
    int length;
    int capacity;
    int position;
};

int bstr_init(struct bstr *b, int length);

int bstr_populate(struct bstr *b, char *s);

struct bstr *bstr_from_str(char *s);

int bstr_realloc(struct bstr *b, int length);

int bstr_concat(struct bstr *b1, struct bstr *b2);

int bstr_extend(struct bstr *b, char *s);

struct bstr *bstr_duplicate(struct bstr *b);

int bstr_read(struct bstr *b, char *buf, int bytes);

void bstr_cleanup(struct bstr *b);

#endif
