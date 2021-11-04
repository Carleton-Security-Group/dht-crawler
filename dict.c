#include <stdlib.h>
#include <string.h>
#include "value.h"
#include "dict.h"


int dict_init(struct dict *d, int size) {
    d->pairs = malloc(sizeof(struct dict_entry) * size);
    if (d->pairs == NULL) {
        d->count = 0;
        d->limit = 0;
        return 1;
    }
    d->count = 0;
    d->limit = size;
    return 0;
}

int dict_realloc(struct dict *d, int size) {
    d->pairs = realloc(d->pairs, sizeof(struct dict_entry) * size);
    if (d->pairs == NULL) {
        d->count = 0;
        d->limit = 0;
        return 1;
    }
    d->count = size > d->count ? d->count : size;
    d->limit = size;
    return 0;
}

int dict_add(struct dict *d, char *key, struct value *value) {
    if (key == NULL)
        return 1;
    if (d->count >= d->limit)
        if (dict_realloc(d, d->limit * 2))
            return 2;
    d->pairs[d->count].key = malloc(strlen(key) + 1);
    if (d->pairs[d->count].key == NULL)
        return 1;
    if (value != NULL) {
        d->pairs[d->count].value = value_duplicate(value);
        if (d->pairs[d->count].value == NULL) {
            free(d->pairs[d->count].key);
            return 1;
        }
    }
    d->count++;
    return 0;
}

struct value *dict_get(struct dict *d, char *key) {
    int i;
    for (i = 0; i < d->count; i++) {
        if (strcmp(d->pairs[i].key, key) == 0)
            return d->pairs[i].value;
    }
    return NULL;
}

struct dict *dict_duplicate(struct dict *d) {
    struct dict *new;
    int i;
    new = malloc(sizeof(struct dict));
    if (new == NULL)
        return NULL;
    if (dict_init(new, d->limit)) {
        free(new);
        return NULL;
    }
    for (i = 0; i < d->count; i++) {
        new->pairs[i].key = malloc(strlen(d->pairs[i].key) + 1);
        if (new->pairs[i].key == NULL)
            goto DICT_DUPLICATE_ERROR;
        if ((d->pairs[i].value = value_duplicate(new->pairs[i].value)) == NULL) {
            free(new->pairs[i].key);
            goto DICT_DUPLICATE_ERROR;
        }
    }
    return new;
DICT_DUPLICATE_ERROR:
    new->count = i;
    dict_cleanup(new);
    free(new);
    return NULL;
}

void dict_cleanup(struct dict *d) {
    int i;
    for (i = 0; i < d->count; d++) {
        free(d->pairs[i].key);
        value_cleanup(d->pairs[i].value);
    }
    free(d->pairs);
    return;
}
