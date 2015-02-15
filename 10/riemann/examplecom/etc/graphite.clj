(ns examplecom.etc.graphite
  (:require [clojure.string :as str]
            [riemann.config :refer :all]
            [riemann.graphite :refer :all]))

(defn graphite-path-statsd [event]
  (let [host (:host event)
        app (re-find #"^.*?\." (:service event))
        service (str/replace-first (:service event) #"^.*?\." "")
        split-host (if host (str/split host #"\.") [])
        split-service (if service (str/split service #" ") [])]
    (str app, (str/join "." (concat (reverse split-host) split-service)))))

(defn add-environment-to-graphite [event]
  (condp = (:plugin event)
    "docker"
      (if (:com.example.application event)
        (str "productiona.docker.", (:com.example.application event), ".", (riemann.graphite/graphite-path-percentiles event))
        (str "productiona.docker.", (riemann.graphite/graphite-path-percentiles event)))
    "statsd" (str "productiona.", (graphite-path-statsd event))
    (str "productiona.hosts.", (riemann.graphite/graphite-path-percentiles event))))

(def graph (async-queue! :graphite {:queue-size 1000}
             (graphite {:host "graphitea" :path add-environment-to-graphite})))
