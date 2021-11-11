#include <stdlib.h>
#include <string.h>
#include "value.h"
#include "dict.h"
#include "list.h"


int value_populate(struct value *old, struct value *new) {
    new->type = old->type;
    switch (old->type) {
    case dict_t:
        new->d = dict_duplicate(old->d);
        if (new->d == NULL)
            return 1;
        break;
    case list_t:
        new->l = list_duplicate(old->l);
        if (new->l == NULL)
            return 1;
        break;
    case string_t:
        new->s = malloc(strlen(old->s) + 1);
        if (new->s == NULL)
            return 1;
        strcpy(new->s, old->s);
    }
    return 0;
}

struct value *value_duplicate(struct value *value) {
    struct value *new = malloc(sizeof(struct value));
    if (new == NULL)
        return NULL;
    if (value_populate(value, new)) {
        free(new);
        return NULL;
    }
    return new;
}

void value_cleanup(struct value *value) {
    switch (value->type) {
    case dict_t:
        dict_cleanup(value->d);
        break;
    case list_t:
        list_cleanup(value->l);
        break;
    case string_t:
        free(value->s);
    }
}
