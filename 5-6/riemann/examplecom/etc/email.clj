(ns examplecom.etc.email
  (:require [riemann.email :refer :all]))

(def email (mailer {:from "riemann@example.com"}))
