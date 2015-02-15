(ns examplecom.etc.count-notifications
    (:require [riemann.streams :refer :all]))

(defn count-notifications
  "Count notifications"
  [& children]
  (adjust [:service #(str % ".rate")]
    (tag "notification-rate"
      (rate 5
        (fn [event]
          (call-rescue event children))))))
