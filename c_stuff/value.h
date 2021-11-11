#ifndef VALUE_H
#define VALUE_H 1

enum value_type {
    dict_t,
    list_t,
    string_t,
};

struct value {
    union {
        struct dict *d;
        struct list *l;
        char *s;
    };
    enum value_type type;
};

int value_populate(struct value *old, struct value *new);

struct value *value_duplicate(struct value *value);

void value_cleanup(struct value *value);

#endif
