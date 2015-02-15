#! /usr/bin/python
#Copyright 2014 Jeremy Carroll
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


import collectd
import json
import urllib2
import socket
import collections
from distutils.version import StrictVersion


ES_CLUSTER = "elasticsearch"
ES_HOST = "localhost"
ES_PORT = 9200

# ES indexes must be fully qualified. E.g. _all, index1,index2
# To do:  Handle glob sytanx for index names.
ES_INDEX = [ ]

ENABLE_INDEX_STATS = False
ENABLE_NODE_STATS = True

VERBOSE_LOGGING = False

Stat = collections.namedtuple('Stat', ('type', 'path'))

# Indices are cluster wide, metrics should be collected from only one server
# in the cluster or from an external probe server.
INDEX_STATS = {

    # === ElasticSearch 0.90.x and higher ===
    "v('{es_version}') >= v('0.90.0')": {

        ## PRIMARIES
        # DOCS
        "indices.{index_name}.primaries.docs.count" : Stat("counter", "indices.%s.primaries.docs.count"),
        "indices.{index_name}.primaries.docs.deleted" : Stat("counter", "indices.%s.primaries.docs.deleted"),
        # STORE
        "indices.{index_name}.primaries.store.size_in_bytes" : Stat("bytes", "indices.%s.primaries.store.size_in_bytes"),
        "indices.{index_name}.primaries.store.throttle_time_in_millis" : Stat("counter", "indices.%s.primaries.store.throttle_time_in_millis"),
        # INDEXING
        "indices.{index_name}.primaries.indexing.index_total" : Stat("counter", "indices.%s.primaries.indexing.index_total"),
        "indices.{index_name}.primaries.indexing.index_time_in_millis" : Stat("counter", "indices.%s.primaries.indexing.index_time_in_millis"),
        "indices.{index_name}.primaries.indexing.index_current" : Stat("gauge", "indices.%s.primaries.indexing.index_current"),
        "indices.{index_name}.primaries.indexing.delete_total" : Stat("counter", "indices.%s.primaries.indexing.delete_total"),
        "indices.{index_name}.primaries.indexing.delete_time_in_millis" : Stat("counter", "indices.%s.primaries.indexing.delete_time_in_millis"),
        "indices.{index_name}.primaries.indexing.delete_current" : Stat("gauge", "indices.%s.primaries.indexing.delete_current"),
        # GET
        "indices.{index_name}.primaries.get.time_in_millis" : Stat("counter", "indices.%s.primaries.get.time_in_millis"),
        "indices.{index_name}.primaries.get.exists_total" : Stat("counter", "indices.%s.primaries.get.exists_total"),
        "indices.{index_name}.primaries.get.exists_time_in_millis" : Stat("counter", "indices.%s.primaries.get.exists_time_in_millis"),
        "indices.{index_name}.primaries.get.missing_total" : Stat("counter", "indices.%s.primaries.get.missing_total"),
        "indices.{index_name}.primaries.get.missing_time_in_millis" : Stat("counter", "indices.%s.primaries.get.missing_time_in_millis"),
        "indices.{index_name}.primaries.get.current" : Stat("gauge", "indices.%s.primaries.get.current"),
        # SEARCH
        "indices.{index_name}.primaries.search.open_contexts" : Stat("gauge", "indices.%s.primaries.search.open_contexts"),
        "indices.{index_name}.primaries.search.query_total" : Stat("counter", "indices.%s.primaries.search.query_total"),
        "indices.{index_name}.primaries.search.query_time_in_millis" : Stat("counter", "indices.%s.primaries.search.query_time_in_millis"),
        "indices.{index_name}.primaries.search.query_current" : Stat("gauge", "indices.%s.primaries.search.query_current"),
        "indices.{index_name}.primaries.search.fetch_total" : Stat("counter", "indices.%s.primaries.search.fetch_total"),
        "indices.{index_name}.primaries.search.fetch_time_in_millis" : Stat("counter", "indices.%s.primaries.search.fetch_time_in_millis"),
        "indices.{index_name}.primaries.search.fetch_current" : Stat("gauge", "indices.%s.primaries.search.fetch_current"),
        # MERGES
        "indices.{index_name}.primaries.merges.current" : Stat("gauge", "indices.%s.primaries.merges.current"),
        "indices.{index_name}.primaries.merges.current_docs" : Stat("gauge", "indices.%s.primaries.merges.current_docs"),
        "indices.{index_name}.primaries.merges.current_size_in_bytes" : Stat("bytes", "indices.%s.primaries.merges.current_size_in_bytes"),
        "indices.{index_name}.primaries.merges.total" : Stat("counter", "indices.%s.primaries.merges.total"),
        "indices.{index_name}.primaries.merges.total_time_in_millis" : Stat("counter", "indices.%s.primaries.merges.total_time_in_millis"),
        "indices.{index_name}.primaries.merges.total_docs" : Stat("counter", "indices.%s.primaries.merges.total_docs"),
        "indices.{index_name}.primaries.merges.total_size_in_bytes" : Stat("bytes", "indices.%s.primaries.merges.total_size_in_bytes"),
        # REFRESH
        "indices.{index_name}.primaries.refresh.total" : Stat("counter", "indices.%s.primaries.refresh.total"),
        "indices.{index_name}.primaries.refresh.total_time_in_millis" : Stat("counter", "indices.%s.primaries.refresh.total_time_in_millis"),
        # FLUSH
        "indices.{index_name}.primaries.flush.total" : Stat("counter", "indices.%s.primaries.flush.total"),
        "indices.{index_name}.primaries.flush.total_time_in_millis" : Stat("counter", "indices.%s.primaries.flush.total_time_in_millis"),
        # WARMER
        "indices.{index_name}.primaries.warmer.current" : Stat("gauge", "indices.%s.primaries.warmer.current"),
        "indices.{index_name}.primaries.warmer.total" : Stat("counter", "indices.%s.primaries.warmer.total"),
        "indices.{index_name}.primaries.warmer.total_time_in_millis" : Stat("counter", "indices.%s.primaries.warmer.total_time_in_millis"),
        # FILTER_CACHE
        "indices.{index_name}.primaries.filter_cache.memory_size_in_bytes" : Stat("bytes", "indices.%s.primaries.filter_cache.memory_size_in_bytes"),
        "indices.{index_name}.primaries.filter_cache.evictions" : Stat("counter", "indices.%s.primaries.filter_cache.evictions"),
        # ID_CACHE
        "indices.{index_name}.primaries.id_cache.memory_size_in_bytes" : Stat("bytes", "indices.%s.primaries.id_cache.memory_size_in_bytes"),
        # FIELDDATA
        "indices.{index_name}.primaries.fielddata.memory_size_in_bytes" : Stat("bytes", "indices.%s.primaries.fielddata.memory_size_in_bytes"),
        "indices.{index_name}.primaries.fielddata.evictions" : Stat("counter", "indices.%s.primaries.fielddata.evictions"),
        # PERCOLATE
        "indices.{index_name}.primaries.percolate.total" : Stat("counter", "indices.%s.primaries.percolate.total"),
        "indices.{index_name}.primaries.percolate.time_in_millis" : Stat("counter", "indices.%s.primaries.percolate.time_in_millis"),
        "indices.{index_name}.primaries.percolate.current" : Stat("gauge", "indices.%s.primaries.percolate.current"),
        "indices.{index_name}.primaries.percolate.memory_size_in_bytes" : Stat("bytes", "indices.%s.primaries.percolate.memory_size_in_bytes"),
        "indices.{index_name}.primaries.percolate.queries" : Stat("counter", "indices.%s.primaries.percolate.queries"),
        # COMPELTION
        "indices.{index_name}.primaries.completion.size_in_bytes" : Stat("bytes", "indices.%s.primaries.completion.size_in_bytes"),
        # SEGMENTS
        "indices.{index_name}.primaries.segments.count" : Stat("counter", "indices.%s.primaries.segments.count"),
        "indices.{index_name}.primaries.segments.memory_in_bytes" : Stat("bytes", "indices.%s.primaries.segments.memory_in_bytes"),
        "indices.{index_name}.primaries.segments.index_writer_memory_in_bytes" : Stat("bytes", "indices.%s.primaries.segments.index_writer_memory_in_bytes"),
        "indices.{index_name}.primaries.segments.version_map_memory_in_bytes" : Stat("bytes", "indices.%s.primaries.segments.version_map_memory_in_bytes"),
        # TRANSLOG
        "indices.{index_name}.primaries.translog.operations" : Stat("counter", "indices.%s.primaries.translog.operations"),
        "indices.{index_name}.primaries.translog.size_in_bytes" : Stat("bytes", "indices.%s.primaries.translog.size_in_bytes"),
        # SUGGEST
        "indices.{index_name}.primaries.suggest.total" : Stat("counter", "indices.%s.primaries.suggest.total"),
        "indices.{index_name}.primaries.suggest.time_in_millis" : Stat("counter", "indices.%s.primaries.suggest.time_in_millis"),
        "indices.{index_name}.primaries.suggest.current" : Stat("gauge", "indices.%s.primaries.suggest.current"),

        ## TOTAL ##
        # DOCS
        "indices.{index_name}.total.docs.count" : Stat("gauge", "indices.%s.total.docs.count"),
        "indices.{index_name}.total.docs.deleted" : Stat("gauge", "indices.%s.total.docs.deleted"),
        # STORE
        "indices.{index_name}.total.store.size_in_bytes" : Stat("gauge", "indices.%s.total.store.size_in_bytes"),
        "indices.{index_name}.total.store.throttle_time_in_millis" : Stat("counter", "indices.%s.total.store.throttle_time_in_millis"),
        # INDEXING
        "indices.{index_name}.total.indexing.index_total" : Stat("counter", "indices.%s.total.indexing.index_total"),
        "indices.{index_name}.total.indexing.index_time_in_millis" : Stat("counter", "indices.%s.total.indexing.index_time_in_millis"),
        "indices.{index_name}.total.indexing.index_current" : Stat("gauge", "indices.%s.total.indexing.index_current"),
        "indices.{index_name}.total.indexing.delete_total" : Stat("counter", "indices.%s.total.indexing.delete_total"),
        "indices.{index_name}.total.indexing.delete_time_in_millis" : Stat("counter", "indices.%s.total.indexing.delete_time_in_millis"),
        "indices.{index_name}.total.indexing.delete_current" : Stat("gauge", "indices.%s.total.indexing.delete_current"),
        # GET
        "indices.{index_name}.total.get.total" : Stat("counter", "indices.%s.total.get.total"),
        "indices.{index_name}.total.get.time_in_millis" : Stat("counter", "indices.%s.total.get.time_in_millis"),
        "indices.{index_name}.total.get.exists_total" : Stat("counter", "indices.%s.total.get.exists_total"),
        "indices.{index_name}.total.get.exists_time_in_millis" : Stat("counter", "indices.%s.total.get.exists_time_in_millis"),
        "indices.{index_name}.total.get.missing_total" : Stat("counter", "indices.%s.total.get.missing_total"),
        "indices.{index_name}.total.get.missing_time_in_millis" : Stat("counter", "indices.%s.total.get.missing_time_in_millis"),
        "indices.{index_name}.total.get.current" : Stat("gauge", "indices.%s.total.get.current"),
        # SEARCH
        "indices.{index_name}.total.search.open_contexts" : Stat("gauge", "indices.%s.total.search.open_contexts"),
        "indices.{index_name}.total.search.query_total" : Stat("counter", "indices.%s.total.search.query_total"),
        "indices.{index_name}.total.search.query_time_in_millis" : Stat("counter", "indices.%s.total.search.query_time_in_millis"),
        "indices.{index_name}.total.search.query_current" : Stat("gauge", "indices.%s.total.search.query_current"),
        "indices.{index_name}.total.search.fetch_total" : Stat("counter", "indices.%s.total.search.fetch_total"),
    }
}

NODE_STATS = {

    # === ElasticSearch 0.90.x and higher ===
    "v('{es_version}') >= v('0.90.0')": {
        ## DOCS
        'indices.docs.count': Stat("gauge", "nodes.%s.indices.docs.count"),
        'indices.docs.deleted': Stat("counter", "nodes.%s.indices.docs.deleted"),

        ## STORE
        'indices.store.size': Stat("bytes", "nodes.%s.indices.store.size_in_bytes"),

        ## INDEXING
        'indices.indexing.index-total': Stat("counter", "nodes.%s.indices.indexing.index_total"),
        'indices.indexing.index-time': Stat("counter", "nodes.%s.indices.indexing.index_time_in_millis"),
        'indices.indexing.delete-total': Stat("counter", "nodes.%s.indices.indexing.delete_total"),
        'indices.indexing.delete-time': Stat("counter", "nodes.%s.indices.indexing.delete_time_in_millis"),
        'indices.indexing.index-current': Stat("gauge", "nodes.%s.indices.indexing.index_current"),
        'indices.indexing.delete-current': Stat("gauge", "nodes.%s.indices.indexing.delete_current"),

        ## GET
        'indices.get.total': Stat("counter", "nodes.%s.indices.get.total"),
        'indices.get.time': Stat("counter", "nodes.%s.indices.get.time_in_millis"),
        'indices.get.exists-total': Stat("counter", "nodes.%s.indices.get.exists_total"),
        'indices.get.exists-time': Stat("counter", "nodes.%s.indices.get.exists_time_in_millis"),
        'indices.get.missing-total': Stat("counter", "nodes.%s.indices.get.missing_total"),
        'indices.get.missing-time': Stat("counter", "nodes.%s.indices.get.missing_time_in_millis"),
        'indices.get.current': Stat("gauge", "nodes.%s.indices.get.current"),

        ## SEARCH
        'indices.search.query-current': Stat("gauge", "nodes.%s.indices.search.query_current"),
        'indices.search.query-total': Stat("counter", "nodes.%s.indices.search.query_total"),
        'indices.search.query-time': Stat("counter", "nodes.%s.indices.search.query_time_in_millis"),
        'indices.search.fetch-current': Stat("gauge", "nodes.%s.indices.search.fetch_current"),
        'indices.search.fetch-total': Stat("counter", "nodes.%s.indices.search.fetch_total"),
        'indices.search.fetch-time': Stat("counter", "nodes.%s.indices.search.fetch_time_in_millis"),

        # JVM METRICS #
        ##GC
        'jvm.gc.time': Stat("counter", "nodes.%s.jvm.gc.collectors.young.collection_time_in_millis"),
        'jvm.gc.count': Stat("counter", "nodes.%s.jvm.gc.collectors.young.collection_count"),
        'jvm.gc.old-time': Stat("counter", "nodes.%s.jvm.gc.collectors.old.collection_time_in_millis"),
        'jvm.gc.old-count': Stat("counter", "nodes.%s.jvm.gc.collectors.old.collection_count"),

        ## MEM
        'jvm.mem.heap-committed': Stat("bytes", "nodes.%s.jvm.mem.heap_committed_in_bytes"),
        'jvm.mem.heap-used': Stat("bytes", "nodes.%s.jvm.mem.heap_used_in_bytes"),
        'jvm.mem.heap-used-percent': Stat("percent", "nodes.%s.jvm.mem.heap_used_percent"),
        'jvm.mem.non-heap-committed': Stat("bytes", "nodes.%s.jvm.mem.non_heap_committed_in_bytes"),
        'jvm.mem.non-heap-used': Stat("bytes", "nodes.%s.jvm.mem.non_heap_used_in_bytes"),

        ## THREADS
        'jvm.threads.count': Stat("gauge", "nodes.%s.jvm.threads.count"),
        'jvm.threads.peak': Stat("gauge", "nodes.%s.jvm.threads.peak_count"),

        # TRANSPORT METRICS #
        'transport.server_open': Stat("gauge", "nodes.%s.transport.server_open"),
        'transport.rx.count': Stat("counter", "nodes.%s.transport.rx_count"),
        'transport.rx.size': Stat("bytes", "nodes.%s.transport.rx_size_in_bytes"),
        'transport.tx.count': Stat("counter", "nodes.%s.transport.tx_count"),
        'transport.tx.size': Stat("bytes", "nodes.%s.transport.tx_size_in_bytes"),

        # HTTP METRICS #
        'http.current_open': Stat("gauge", "nodes.%s.http.current_open"),
        'http.total_open': Stat("counter", "nodes.%s.http.total_opened"),

        # PROCESS METRICS #
        'process.open_file_descriptors': Stat("gauge", "nodes.%s.process.open_file_descriptors"),
    },

    # === ElasticSearch 0.90.x only ===
    "v('0.90.0') <= v('{es_version}') < v('1.0.0')": {
        ##CPU
        'process.cpu.percent': Stat("gauge", "nodes.%s.process.cpu.percent")
    },

    # === ElasticSearch 1.0.0 or greater ===
    "v('{es_version}') >= v('1.0.0')": {
        ## STORE
        'indices.store.throttle-time': Stat("counter", "nodes.%s.indices.store.throttle_time_in_millis"),

        ##SEARCH
        'indices.search.open-contexts': Stat("gauge", "nodes.%s.indices.search.open_contexts"),

        ##CACHE
        'indices.cache.field.eviction': Stat("counter", "nodes.%s.indices.fielddata.evictions"),
        'indices.cache.field.size': Stat("bytes", "nodes.%s.indices.fielddata.memory_size_in_bytes"),
        'indices.cache.filter.evictions': Stat("counter", "nodes.%s.indices.filter_cache.evictions"),
        'indices.cache.filter.size': Stat("bytes", "nodes.%s.indices.filter_cache.memory_size_in_bytes"),

        ## FLUSH
        'indices.flush.total': Stat("counter", "nodes.%s.indices.flush.total"),
        'indices.flush.time': Stat("counter", "nodes.%s.indices.flush.total_time_in_millis"),

        ## MERGES
        'indices.merges.current': Stat("gauge", "nodes.%s.indices.merges.current"),
        'indices.merges.current-docs': Stat("gauge", "nodes.%s.indices.merges.current_docs"),
        'indices.merges.current-size': Stat("bytes", "nodes.%s.indices.merges.current_size_in_bytes"),
        'indices.merges.total': Stat("counter", "nodes.%s.indices.merges.total"),
        'indices.merges.total-docs': Stat("gauge", "nodes.%s.indices.merges.total_docs"),
        'indices.merges.total-size': Stat("bytes", "nodes.%s.indices.merges.total_size_in_bytes"),
        'indices.merges.time': Stat("counter", "nodes.%s.indices.merges.total_time_in_millis"),

        ## REFRESH
        'indices.refresh.total': Stat("counter", "nodes.%s.indices.refresh.total"),
        'indices.refresh.time': Stat("counter", "nodes.%s.indices.refresh.total_time_in_millis"),

        ## SEGMENTS
        'indices.segments.count': Stat("gauge", "nodes.%s.indices.segments.count"),
        'indices.segments.size': Stat("bytes", "nodes.%s.indices.segments.memory_in_bytes"),

        ## TRANSLOG
        'indices.translog.operations': Stat("gauge", "nodes.%s.indices.translog.operations"),
        'indices.translog.size': Stat("bytes", "nodes.%s.indices.translog.size_in_bytes"),
    },

    # DICT: ElasticSearch 1.3.0 or greater
    "v('{es_version}') >= v('1.3.0')": {
        'indices.segments.index-writer-memory': Stat("bytes", "nodes.%s.indices.segments.index_writer_memory_in_bytes"),
        'indices.segments.index-memory': Stat("bytes", "nodes.%s.indices.segments.memory_in_bytes"),
    }
}

STATS_CUR = {}

def check_es_version(rule, version):
    log_verbose('Elasticsearch version rule: %s' % (rule.format(es_version=version)) )
    v = StrictVersion
    eval_string = rule.format(es_version=version)
    return eval(eval_string)


def generate_metric_set(rules, es_version):
    """
    @breif - Given an initial set of metrics with the elasticsearch version and the
    requested metrics to be fetched, parse all pre-defined metrics and
    return a sythesised set of metrics which is compatiable with existing
    functions.

    @rules - a struction which contains a rule to be evaluated when evaluting
    which metrics to be appended to the returned data set.

    @es_version - the Elasticsearch version.
    """
    synthesised_metrics = {}

    for k in rules.keys():
        if check_es_version(k, es_version):
            log_verbose("Adding %s" % k)
            synthesised_metrics.update(rules[k])

    return synthesised_metrics


# FUNCTION: Collect stats from JSON result
def lookup_node_stat(stat, metrics, json):
    node = json['nodes'].keys()[0]
    val = dig_it_up(json, metrics[stat].path % node)

    # Check to make sure we have a valid result
    # dig_it_up returns False if no match found
    if not isinstance(val, bool):
        return int(val)
    else:
        return None


def lookup_index_stat(stat, metrics, json):
    indices = json['indices'].keys()

    for index in indices:
        formatted_stat = stat.format(index_name=index)
        val = index_dig_it_up(json, metrics[stat].path, index )

    # Check to make sure we have a valid result
    # dig_it_up returns False if no match found
    if not isinstance(val, bool):
        return int(val)
    else:
        return None


def log_verbose(msg):
    if VERBOSE_LOGGING == True:
        collectd.warning('elasticsearch plugin [verbose]: %s' % msg)


def configure_callback(conf):
    """Received configuration information"""
    global ES_HOST, ES_PORT, VERBOSE_LOGGING, ES_CLUSTER, ES_INDEX, ENABLE_INDEX_STATS, ENABLE_NODE_STATS
    for node in conf.children:
        if node.key == 'Host':
            ES_HOST = node.values[0]
        elif node.key == 'Port':
            ES_PORT = int(node.values[0])
        elif node.key == 'Verbose':
            VERBOSE_LOGGING = bool(node.values[0])
        elif node.key == 'Cluster':
            ES_CLUSTER = node.values[0]
        elif node.key == 'Indexes':
            ES_INDEX = node.values
            log_verbose('Indexes to query: %s' % (str(ES_INDEX)))
        elif node.key == 'EnableIndexStats':
            ENABLE_INDEX_STATS = bool(node.values[0])
            log_verbose("Enable Index Stats : %s" % ENABLE_INDEX_STATS)
        elif node.key == 'EnableNodeStats':
            ENABLE_NODE_STATS = bool(node.values[0])
            log_verbose("Enable Node Stats : %s" % ENABLE_NODE_STATS)
        else:
            collectd.warning('elasticsearch plugin: Ignoring unknown config key: %s.' % node.key)

    log_verbose('Configured with host=%s, port=%s' % (ES_HOST, ES_PORT))



def fetch_url(url):
    try:
        result = json.load(urllib2.urlopen(url, timeout=10))
    except urllib2.URLError, e:
        collectd.error('elasticsearch plugin: Error connecting to %s - %r' % (url, e))
        return None
    return result



def fetch_stats():
    global ES_CLUSTER, ES_HOST, ES_PORT, STATS_CUR, ES_INDEX, ENABLE_NODE_STATS, ENABLE_INDEX_STATS

    NODE_STATS_URL = {
        "v('{es_version}') >= v('0.90.0')": '{url}_cluster/nodes/_local/stats?http=true&process=true&jvm=true&transport=true',
        "v('{es_version}') >= v('1.0.0')" : '{url}_nodes/_local/stats/transport,http,process,jvm,indices'
    }

    node_stats_url = ""
    base_url = 'http://' + ES_HOST + ':' + str(ES_PORT) + '/'
    server_info = fetch_url(base_url)
    version = server_info['version']['number']

    # Get the cluster name.
    if server_info.has_key("cluster_name"):
        ES_CLUSTER = server_info["cluster_name"]
    else:
        ES_CLUSTER = fetch_url(base_url+"_nodes")['cluster_name']

    log_verbose('Elasticsearch cluster: %s version : %s' % (ES_CLUSTER, version))

    # Node statistics
    if ENABLE_NODE_STATS:
        node_metrics = {}
        for k in NODE_STATS_URL.keys():
            if check_es_version(k, str(version)):
                node_stats_url = NODE_STATS_URL[k].format(url=base_url)
        log_verbose('Node url : %s' % node_stats_url)

        node_metrics.update(generate_metric_set(NODE_STATS, version))

# FIXME: Re-add the thread pool statistics.
#        # add info on thread pools
#        for pool in ['generic', 'index', 'get', 'snapshot', 'merge', 'optimize', 'bulk', 'warmer', 'flush', 'search', 'refresh']:
#            for attr in ['threads', 'queue', 'active', 'largest']:
#                path = 'thread_pool.{0}.{1}'.format(pool, attr)
#                node_metrics[path] = Stat("gauge", 'nodes.%s.{0}'.format(path))
#            for attr in ['completed', 'rejected']:
#                path = 'thread_pool.{0}.{1}'.format(pool, attr)
#                node_metrics[path] = Stat("counter", 'nodes.%s.{0}'.format(path))

        node_json = fetch_url(node_stats_url)
        parse_node_stats(node_metrics, node_json)
    log_verbose('Node stats processed')

    # Indexes statistics
    if ENABLE_INDEX_STATS:
        index_metrics = {}
        log_verbose('Checking index.')
        for k in ES_INDEX:
            index_stats_url = base_url + k + "/_stats"
            index_metrics.update(generate_metric_set(INDEX_STATS, version))
            log_verbose('Index statistics url : %s' % index_stats_url)

            index_json = fetch_url(index_stats_url)
            parse_index_stats(index_metrics, index_json, k)

    return True



def parse_node_stats(metrics, json):
    """Parse stats response from ElasticSearch"""
    for name, key in metrics.iteritems():
        result = lookup_node_stat(name, metrics, json)
        dispatch_stat(result, name, key)
    return True


def parse_index_stats(metrics, json, index):
    """Parse stats response from ElasticSearch"""
    for name, key in metrics.iteritems():
        result = lookup_index_stat(name, metrics, json)
        dispatch_stat(result, name.format(index_name=index), key)
    return True


def dispatch_stat(result, name, key):
    """Read a key from info response data and dispatch a value"""
    if result is None:
        collectd.warning('elasticsearch plugin: Value not found for %s' % name)
        return
    estype = key.type
    value = int(result)
    log_verbose('Sending value[%s]: %s=%s' % (estype, name, value))

    val = collectd.Values(plugin='elasticsearch')
    val.plugin_instance = ES_CLUSTER
    val.type = estype
    val.type_instance = name
    val.values = [value]
    val.meta={'0': True}
    val.dispatch()


def read_callback():
    log_verbose('Read callback called')
    stats = fetch_stats()



def dig_it_up(obj, path):
    try:
        if type(path) in (str, unicode):
            path = path.split('.')
            return reduce(lambda x, y: x[y], path, obj)
    except:
        return False


def index_dig_it_up(obj, path, index_name):
    try:
        if type(path) in (str, unicode):
            path = path.split('.')
            path[1] = path[1] % index_name
            return reduce(lambda x, y: x[y], path, obj)
    except:
        return False



collectd.register_config(configure_callback)
collectd.register_read(read_callback)
