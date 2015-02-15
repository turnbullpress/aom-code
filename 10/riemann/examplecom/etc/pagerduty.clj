(ns examplecom.etc.pagerduty
    (:require [riemann.pagerduty :refer :all]
              [riemann.streams :refer :all]))

(defn pd-format
  [event]
  {:incident_key (str (:host event) " " (:service event))
   :description (str "Host: " (:host event) " "
                     (:service event) " is "
                     (:state event) " ("
                     (:metric event) ")")
   :details (assoc event :graphs (str "http://graphitea.example.com:3000/dashboard/script/riemann.js?host="(:host event)))})

(def pd (pagerduty { :service-key "123ABC123" :formatter pd-format}))

(defn page
  []
  (changed-state {:init "ok"}
    (where (state "ok")
    (:resolve pd)
    (else (:trigger pd)))))
