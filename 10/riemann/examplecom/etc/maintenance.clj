(ns examplecom.etc.maintenance
  (:require [riemann.streams :refer :all]))

(defn maintenance-mode?
  "Is it currently in maintenance mode?"
  [event]
  (->> '(and (= host (:host event))
             (= service (:service event))
             (= (:type event) "maintenance-mode"))
       (riemann.index/search (:index @core))
       first
       :state
       (= "active")))
