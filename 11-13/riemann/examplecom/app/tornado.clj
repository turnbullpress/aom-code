(ns examplecom.app.tornado
  "Monitoring streams for Tornado"
  (:require [riemann.config :refer :all]
            [clojure.tools.logging :refer :all]
            [riemann.folds :as folds]
            [riemann.streams :refer :all]))

(defn alert_graph
  []
  "Alert and graph on events"
  (sdo
    (changed-state {:init "ok"}
      (where (state "critical")
        (page))
      (where (state "warning")
        (slacker)))
    (smap rewrite-service graph)))

(defn webtier
  "Checks for the Tornado Web Tier"
  []
  (let [active_servers 2.0]
    (sdo
      (where (and (service "haproxy/gauge-backend.tornado-web.active_servers")
                  (< metric active_servers))
        (adjust #(assoc % :service "tornado-web active servers"
                          :type_instance nil
                          :state (condp = (:metric %)
                                   0.0 "critical"
                                   1.0 "warning"
                                   2.0 "ok"))
          (changed :metric {:init active_servers}
            (slacker))))
      (check_ratio "haproxy/derive-frontend.tornado-www.response_5xx"
                   "haproxy/derive-frontend.tornado-www.request_total"
                   "haproxy.frontend.tornado-www.5xx_error_percentage"
                   0.5 1
        (alert_graph)))))

(defn apptier
  "Checks for the Tornado App Tier"
  []
  (sdo
    (where (service "curl_json-tornado-api/gauge-price")
      (where (!= metric 666)
        (slacker))
      (expired
        (page)))
    (where (service #"^tornado.api.")
      (smap rewrite-service graph))
    (check_ratio "GenericJMX-memory-heap/memory-used"
                 "GenericJMX-memory-heap/memory-max"
                 "jmx.memory-heap.percentage_used"
                 80 90
      (alert_graph))
    (where (service "tornado.api.request")
      (with { :service "tornado.api.request.rate" :metric 1 }
        (rate 1
          (smap rewrite-service graph))))
    (check_percentiles "tornado.api.request" 10
      (smap rewrite-service graph)
      (where (and (service "tornado.api.request 0.99") (>= metric 100.0))
        (changed-state { :init "ok"}
          (slacker))))))

(defn datatier
  "Check for the Tornado Data Tier"
  []
  (sdo
    (check_ratio "mysql-status/gauge-Max_used_connections"
                 "mysql-variables/gauge-max_connections"
                 "mysql.max_connection_percentage"
                   80 90
        (alert_graph))
    (create_rate "mysql-status/counter-Aborted_connects" 5)
    (check_percentiles "dbi-performance_schema/gauge-insert_query_time" 10
      (smap rewrite-service graph)
      (where (and (service "dbi-performance_schema/gauge-insert_query_time 0.99") (>= metric 3.0))
        (changed-state { :init "ok"}
          (slacker))))))

(defn checks
  "Handles events for Tornado"
  []
  (let [web-tier-hosts #"tornado-(proxy|web1|web2)"
        app-tier-hosts #"tornado-(api1|api2)"
        db-tier-hosts #"tornado-(db|redis)"]

    (splitp re-matches host
      web-tier-hosts (webtier)
      app-tier-hosts (apptier)
      db-tier-hosts  (datatier)
      #(info "Catchall" (:host %)))))
