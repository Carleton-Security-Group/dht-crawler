#ifndef LIST_H
#define LIST_H 1

#include "value.h"


struct list {
    struct value *entries;
    int length;
    int capacity;
};

int list_init(struct list *l, int size);

int list_realloc(struct list *l, int size);

int list_add(struct list *l, char *key, struct value *value);

struct value *list_get(struct list *l, int index);

struct list *list_duplicate(struct list *l);

void list_cleanup(struct list *l);

#endif
