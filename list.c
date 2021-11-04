#include <stdlib.h>
#include "value.h"
#include "list.h"


int list_init(struct list *l, int size) {
    l->entries = malloc(sizeof(struct value) * size);
    if (l->entries == NULL) {
        l->count = 0;
        l->limit = 0;
        return 1;
    }
    l->count = 0;
    l->limit = size;
    return 0;
}

int list_realloc(struct list *l, int size) {
    l->entries = realloc(l->entries, sizeof(struct value) * size);
    if (l->entries == NULL) {
        l->count = 0;
        l->limit = 0;
        return 1;
    }
    l->count = size > l->count ? l->count : size;
    l->limit = size;
    return 0;
}

int list_add(struct list *l, char *key, struct value *value) {
    if (l->count >= l->limit)
        if (list_realloc(l, l->limit * 2))
            return 2;
    if (value_populate(value, l->entries + l->count))
        return 1;
    l->count++;
    return 0;
}

struct value *list_get(struct list *l, int index) {
    if (index > l->count || index < 0)
        return NULL;
    return l->entries + index;
}

struct list *list_duplicate(struct list *l) {
    struct list *new;
    int i;
    new = malloc(sizeof(struct list));
    if (new == NULL)
        return NULL;
    if (list_init(new, l->limit)) {
        free(new);
        return NULL;
    }
    for (i = 0; i < l->count; i++) {
        if (value_populate(list_get(l, i), list_get(new, i))) {
            new->count = i;
            list_cleanup(new);
            free(new);
            return NULL;
        }
    }
    return new;
}

void list_cleanup(struct list *l) {
    int i;
    for (i = 0; i < l->count; i++)
        value_cleanup(list_get(l, i));
    free(l->entries);
    return;
}
