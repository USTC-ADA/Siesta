#ifndef LIBHASH_H
#define LIBHASH_H

#include <stdio.h>
#include <stdint.h>

#define LIBHASH_VERSION "0.1.1"

#ifdef __cplusplus
extern "C" {
#endif

struct hash {
    int bucket;
    void *opaque_list;
    void (*destory)(void *val);
};

struct hash *hash_create(int bucket);
void hash_destroy(struct hash *h);
void hash_set_destory(struct hash *h, void (*destory)(void *val));

uint32_t hash_gen32(const char *key, size_t len);
void *hash_get(struct hash *h, const char *key);
void *hash_get32(struct hash *h, uint32_t key);
int hash_set(struct hash *h, const char *key, void *val);
int hash_set32(struct hash *h, uint32_t key, void *val);
int hash_del(struct hash *h, const char *key);
int hash_del32(struct hash *h, uint32_t key);
void *hash_get_and_del(struct hash *h, const char *key);
void *hash_get_and_del32(struct hash *h, uint32_t key);
void hash_dump_all(struct hash *h, int *num, char **key, void **val);
int hash_get_all_cnt(struct hash *h);

#ifdef __cplusplus
}
#endif
#endif

