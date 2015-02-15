(ns examplecom.etc.graphite
  (:require [clojure.string :as str]
            [riemann.config :refer :all]
            [riemann.graphite :refer :all]))

(defn add-environment-to-graphite [event]
  (condp = (:plugin event)
    "docker"
      (if (:com.example.application event)
        (str "productiona.docker.", (:com.example.application event), ".", (riemann.graphite/graphite-path-percentiles event))
        (str "productiona.docker.", (riemann.graphite/graphite-path-percentiles event)))
    (str "productiona.hosts.", (riemann.graphite/graphite-path-percentiles event))))

(def graph (async-queue! :graphite {:queue-size 1000}
  (graphite {:host "graphitea" :path add-environment-to-graphite})))
