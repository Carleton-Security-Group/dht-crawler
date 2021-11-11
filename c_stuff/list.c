#include <stdlib.h>
#include "value.h"
#include "list.h"


int list_init(struct list *l, int size) {
    l->entries = malloc(sizeof(struct value) * size);
    if (l->entries == NULL) {
        l->length = 0;
        l->capacity = 0;
        return 1;
    }
    l->length = 0;
    l->capacity = size;
    return 0;
}

int list_realloc(struct list *l, int size) {
    l->entries = realloc(l->entries, sizeof(struct value) * size);
    if (l->entries == NULL) {
        l->length = 0;
        l->capacity = 0;
        return 1;
    }
    l->length = size > l->length ? l->length : size;
    l->capacity = size;
    return 0;
}

int list_add(struct list *l, char *key, struct value *value) {
    if (l->length >= l->capacity)
        if (list_realloc(l, l->capacity * 2))
            return 2;
    if (value_populate(value, l->entries + l->length))
        return 1;
    l->length++;
    return 0;
}

struct value *list_get(struct list *l, int index) {
    if (index > l->length || index < 0)
        return NULL;
    return l->entries + index;
}

struct list *list_duplicate(struct list *l) {
    struct list *new;
    int i;
    new = malloc(sizeof(struct list));
    if (new == NULL)
        return NULL;
    if (list_init(new, l->capacity)) {
        free(new);
        return NULL;
    }
    for (i = 0; i < l->length; i++) {
        if (value_populate(list_get(l, i), list_get(new, i))) {
            new->length = i;
            list_cleanup(new);
            free(new);
            return NULL;
        }
    }
    return new;
}

void list_cleanup(struct list *l) {
    int i;
    for (i = 0; i < l->length; i++)
        value_cleanup(list_get(l, i));
    free(l->entries);
    return;
}
