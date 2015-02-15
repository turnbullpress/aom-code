(ns examplecom.etc.collectd
  (:require [clojure.tools.logging :refer :all]
            [riemann.streams :refer :all]
            [clojure.string :as str]))

(def default-services
  [{:service #"^load/load/(.*)$" :rewrite "load $1"}
   {:service #"^swap/percent-(.*)$" :rewrite "swap $1"}
   {:service #"^memory/percent-(.*)$" :rewrite "memory $1"}
   {:service #"^processes/ps_state-(.*)$" :rewrite "processes $1"}
   {:service #"^cpu/percent-(.*)$" :rewrite "cpu $1"}
   {:service #"^df-(.*)/(df_complex|percent_bytes)-(.*)$" :rewrite "df $1 $2 $3"}
   {:service #"^interface-(.*)/if_(errors|packets|octets)/(tx|rx)$" :rewrite "nic $1 $3 $2"}])

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
