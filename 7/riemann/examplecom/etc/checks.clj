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
