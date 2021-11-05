#include <stdlib.h>
#include <string.h>
#include "bstr.h"

int bstr_init(struct bstr *b, int length) {
    b->s = malloc(length + 1);
    if (b->s == NULL) {
        b->length = 0;
        b->capacity = 0;
        b->position = 0;
        return 1;
    }
    b->length = 0;
    b->capacity = length;
    b->position = 0;
    return 0;
}

int bstr_populate(struct bstr *b, char *s) {
    if (bstr_init(b, strlen(s)))
        return 1;
    strcpy(b->s, s);
    return 0;
}

struct bstr *bstr_from_str(char *s) {
    struct bstr *new = malloc(sizeof(struct bstr));
    if (new == NULL)
        return NULL;
    if (bstr_populate(new, s)) {
        free(new);
        return NULL;
    }
    return new;
}

int bstr_realloc(struct bstr *b, int length) {
    b->s = realloc(b->s, length + 1);
    if (b->s == NULL) {
        b->length = 0;
        b->capacity = 0;
        b->position = 0;
        return 1;
    }
    b->length = length > b->length ? b->length : length;
    b->capacity = length;
    return 0;
}

int bstr_concat(struct bstr *b1, struct bstr *b2) {
    int orig_length = b1->length, new_length;
    if ((new_length = orig_length + b2->length) > b1->capacity)
        if (bstr_realloc(b1, new_length))
            return 1;
    memcpy(b1->s + orig_length, b2->s, b2->length);
    b1->s[new_length] = '\0';
    b1->length = new_length;
    return 0;
}

int bstr_extend(struct bstr *b, char *s) {
    struct bstr tmp;
    tmp.s = s;
    tmp.length = strlen(s);
    return bstr_concat(b, &tmp);
}

struct bstr *bstr_duplicate(struct bstr *b) {
    struct bstr *new = malloc(sizeof(struct bstr));
    if (new == NULL)
        return NULL;
    if (bstr_init(new, b->capacity)) {
        free(new);
        return NULL;
    }
    strcpy(new->s, b->s);
    new->length = b->length;
    new->position = b->position;
    return new;
}

int bstr_read(struct bstr *b, char *buf, int bytes) {
    int start = b->position;
    int end = b->position + bytes < b->length ? b->position + bytes : b->length;
    while (b->position < end) {
        buf[b->position - start] = b->s[b->position];
        b->position++;
    }
    return end - start;
}

void bstr_cleanup(struct bstr *b) {
    free(b->s);
}
