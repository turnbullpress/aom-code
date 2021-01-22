(ns examplecom.etc.email
  (:require [clojure.string :as str]
            [riemann.email :refer :all]))

(defn format-subject
  "Format the email subject"
  [events]
  (apply format "Service %s is in state %s on host %s" (str/join ", " (map :service events)) (str/join ", " (map :state events)) (map :host events)))

(def header "Monitoring notification from Riemann!\n\n")
(def footer "This is an automated Riemann notification. Please do not reply.")

(defn lookup
  "Lookup events in the index"
  [host service]
  (riemann.index/lookup (:index @riemann.config/core) host service))

(defn round
  "Round numbers to 2 decimal places"
  [metric]
  (clojure.pprint/cl-format nil "~,2f" metric))

(defn byte-to-gb [bytes] (/ bytes (* 1024.0 1024.0 1024.0)))

(defn context
  "Add some contextual event data"
  [event]
  (str
    "Host context:\n"
    "  CPU Utilization:\t"(round (+ (:metric (lookup (:host event) "cpu/percent-system")) (:metric (lookup (:host event) "cpu/percent-user")))) "%\n"
    "  Memory Used:\t"(round (:metric (lookup (:host event) "memory/percent-used"))) "%\n"
    "  Disk(root) %:\t\t"(round (:metric (lookup (:host event) "df-root/percent_bytes-used"))) "% used "
    "  ("(round (byte-to-gb (:metric (lookup (:host event) "df-root/df_complex-used")))) " GB used of "
       (round (+ (byte-to-gb (:metric (lookup (:host event) "df-root/df_complex-used")))
                 (byte-to-gb (:metric (lookup (:host event) "df-root/df_complex-free")))
                 (byte-to-gb (:metric (lookup (:host event) "df-root/df_complex-reserved"))))) "GB)\n\n"
    "Grafana Dashboard:\n\n"
    "  http://graphitea.example.com:3000/dashboard/script/riemann.js?host="(:host event)"\n\n"))

(defn format-body
  "Format the email body"
  [events]
  (str/join "\n\n\n"
        (map
          (fn [event]
            (str
              header
              "Time:\t\t" (riemann.common/time-at (:time event)) "\n"
              "Host:\t\t" (:host event) "\n"
              "Service:\t\t" (:service event) "\n"
              "State:\t\t" (:state event) "\n"
              "Metric:\t\t" (if (ratio? (:metric event))
                (double (:metric event))
                (:metric event)) "\n"
              "Tags:\t\t[" (str/join ", " (:tags event)) "] \n"
              "\n"
              "Description:\t\t" (:description event)
              "\n\n"
              (context event)
              footer))
          events)))

(def email (mailer {:from "riemann@example.com"
                    :subject (fn [events] (format-subject events))
                    :body (fn [events] (format-body events))
                    }))
