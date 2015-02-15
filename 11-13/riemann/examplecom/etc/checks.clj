(ns examplecom.etc.checks
  (:require [riemann.config :refer :all]
            [clojure.tools.logging :refer :all]
            [riemann.streams :refer :all]))

(defn set_state [warning critical]
  (fn [event]
     (assoc event :state
        (condp < (:metric event)
                  critical "critical"
                  warning "warning"
                  "ok"))))

(defn create_rate [srv window]
  (where (service srv)
    (with {:service (str srv " rate")}
      (rate window (smap rewrite-service graph)))))

(defn check_ratio [srv1 srv2 newsrv warning critical & children]
  "Checks the ratio between two events"
  (project [(service srv1)
            (service srv2)]
    (smap folds/quotient-sloppy
      (fn [event] (let [percenta (* (float (:metric event)) 100)
                        new-event (assoc event :metric percenta
                                               :service (str newsrv)
                                               :type_instance nil
                                               :state (condp < percenta
                                                               critical "critical"
                                                               warning  "warning"
                                                                        "ok"))]
          (call-rescue new-event children))))))

(defn check_threshold [srv window func warning critical & children]
  (where (service srv)
    (fixed-time-window window
      (smap func
        (where (< warning metric)
          (smap (set_state warning critical)
            (fn [event]
              (call-rescue event children))))))))

(defn check_percentiles [srv window & children]
  (where (service srv)
    (percentiles window [0.5 0.95 0.99 1]
      (fn [event]
        (call-rescue event children)))))
