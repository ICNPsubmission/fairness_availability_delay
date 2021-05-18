static void
xlate_select_group(struct xlate_ctx *ctx, struct group_dpif *group)
{
    struct flow_wildcards *wc = &ctx->xout->wc;
    const struct ofputil_bucket *bucket;
    uint32_t basis;
    ctx->xout->slow |= SLOW_CONTROLLER;
    const uint32_t p[4] = { ctx->xin->flow.nw_src, ctx->xin->flow.nw_dst, (uint32_t) ctx->xin->flow.tp_src, (uint32_t) ctx->xin->flow.tp_dst }
    size_t n = 4
    basis = hash_words(p,n,0)
    bucket = group_best_live_bucket(ctx, group, basis);
    if (bucket) {
        memset(&wc->masks.dl_dst, 0xff, sizeof wc->masks.dl_dst);
        xlate_group_bucket(ctx, bucket);
    }
}

static const struct ofputil_bucket *
group_best_live_bucket(const struct xlate_ctx *ctx,
                   const struct group_dpif *group,
                   uint32_t basis)
{
    sum = 0;
    const struct ofputil_bucket *bucket = NULL;
    const struct list *buckets;
    if (bucket_is_alive(ctx, bucket, 0)) {
        sum += bucket->weight;
    }
    basis_modulus = basis % sum
    sum=0
    group_dpif_get_buckets(group, &buckets);
    LIST_FOR_EACH (bucket, list_node, buckets) {
        if (bucket_is_alive(ctx, bucket, 0)) {
            sum += bucket->weight;
            if (basis_modulus <= sum) {
                return bucket;
            }
        }
    }
    return bucket;
}
