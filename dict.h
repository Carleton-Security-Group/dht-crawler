#ifndef DICT_H
#define DICT_H 1

#include "value.h"


struct dict_entry {
    char *key;
    struct value *value;
};

struct dict {
    struct dict_entry *pairs;
    int count;
    int limit;
};

int dict_init(struct dict *d, int size);

int dict_realloc(struct dict *d, int size);

int dict_add(struct dict *d, char *key, struct value *value);

struct value *dict_get(struct dict *d, char *key);

struct dict *dict_duplicate(struct dict *d);

void dict_cleanup(struct dict *d);

#endif
