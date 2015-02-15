(ns examplecom.etc.collectd
  (:require [clojure.tools.logging :refer :all]
            [riemann.streams :refer :all]
            [clojure.string :as str]
            [clojure.walk :as walk]))

(defn docker-attribute-map
  [attributes]
  (let [instance (str/split (str/replace attributes #"^.*\[(.*)\]$" "$1") #",")]
    (walk/keywordize-keys (into {} (for [pair instance] (apply hash-map (str/split pair #"=")))))))

(defn docker-attributes
  [{:keys [plugin_instance] :as event}]
  (if-let [attributes (re-find #"^.*\[.*\]$" plugin_instance)]
    (merge event (docker-attribute-map attributes))
    event))

(defn parse-docker-service-host
  [{:keys [type type_instance plugin_instance] :as event}]
  (let [host (re-find #"^\w+\.?\w+\.?\w+" (:plugin_instance event))
        service (cond-> (str (:type event)) (:type_instance event) (str "." (:type_instance event)))]
    (assoc event :service service :host host)))

(defn plugin-map
  "Parses labels from collectd plugin_stance"
  [plugin_instance]
  (let [instance (str/split (str/replace plugin_instance #"^.*\[(.*)\]$" "$1") #",")]
    (walk/keywordize-keys (into {} (for [pair instance] (apply hash-map (str/split pair #"=")))))))

(defn parse-docker
  [& children]
  "Parses Docker events"
  (fn [event]
    (let [host (re-find #"^\w+\.?\w+\.?\w+" (:plugin_instance event))
          service (cond-> (str (:type event)) (:type_instance event) (str "." (:type_instance event)))
          event (assoc event :service service :host host)
          event (merge event (plugin-map (:plugin_instance event)))]
      (call-rescue event children))))

(def default-services
  [{:service #"^load/load/(.*)$" :rewrite "load $1"}
   {:service #"^swap/percent-(.*)$" :rewrite "swap $1"}
   {:service #"^memory/percent-(.*)$" :rewrite "memory $1"}
   {:service #"^processes/ps_state-(.*)$" :rewrite "processes $1"}
   {:service #"^processes-(.*)/(.*)$" :rewrite "processes $1 $2"}
   {:service #"^cpu/percent-(.*)$" :rewrite "cpu $1"}
   {:service #"^df-(.*)/(df_complex|percent_bytes)-(.*)$" :rewrite "df $1 $2 $3"}
   {:service #"^interface-(.*)/if_(errors|packets|octets)/(tx|rx)$" :rewrite "nic $1 $3 $2"}
   {:service #"^protocols-(.*)/(.*)$" :rewrite "protocols $1 $2"}
   {:service #"^GenericJMX-(:?_|\/)?(.*)$" :rewrite "jmx $2"}
   {:service #"^haproxy\/(gauge|derive)-(.*)$" :rewrite "haproxy $2"}
   {:service #"^statsd\/(gauge|derive|latency)-(.*)$" :rewrite "$2"}
   {:service #"^statsd\/(gauge|derive|latency)-(.*)$" :rewrite "statsd $1 $2"}
   {:service #"^mysql-(.*)\/(counter|gauge)-(.*)$" :rewrite "mysql $1 $3"}
   {:service #"^dbi-(.*)\/(gauge|counter)-(.*)$" :rewrite "dbi $1 $3"}
   {:service #"^redis-(.*)$" :rewrite "redis $1"}])

(defn rewrite-service-with
  [rules]
  (let [matcher (fn [s1 s2] (if (string? s1) (= s1 s2) (re-find s1 s2)))]
    (fn [{:keys [service] :as event}]
      (or
       (first
        (for [{:keys [rewrite] :as rule} rules
              :when (matcher (:service rule) service)]
          (assoc event :service
                 (if (string? (:service rule))
                   rewrite
                   (str/replace service (:service rule) rewrite)))))
       event))))

(def rewrite-service
  (rewrite-service-with default-services))
