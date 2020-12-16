#lang rosette/safe

(require rosette/lib/match)
(require rosette/lib/angelic)
(require rosette/lib/synthax)

;;; DSL
(define-symbolic x1 x2 x3 x4 x5 x6 x7 k integer?)

; The syntax of the DSL.
(struct plus (left right) #:transparent)
(struct minus (left right) #:transparent)
(struct ite (bool left right) #:transparent)
(struct And (left right) #:transparent)
(struct Or (left right) #:transparent)
(struct Not (term) #:transparent)
(struct le (left right) #:transparent)
(struct eq (left right) #:transparent)
(struct ge (left right) #:transparent)
(struct lt (left right) #:transparent)
(struct gt (left right) #:transparent)

; The semantics of the DSL.
(define (interpret p)
  (match p
    [(plus a b) (+ (interpret a) (interpret b))]
    [(minus a b) (- (interpret a) (interpret b))]
    [(ite c a b) (if (interpret c) (interpret a) (interpret b))]
    [(And a b) (and (interpret a) (interpret b))]
    [(Or a b) (or (interpret a) (interpret b))]
    [(Not a) (not (interpret a))]
    [(le a b) (<= (interpret a) (interpret b))]
    [(eq a b) (= (interpret a) (interpret b))]
    [(ge a b) (>= (interpret a) (interpret b))]
    [(lt a b) (< (interpret a) (interpret b))]
    [(gt a b) (> (interpret a) (interpret b))]
    [_ p]))

; (define (ans i1 i2) (ite1 (le1 i1 i2) i2 i1))
; (displayln (interpret (ans 5 4)))

;;; SyGuS
(displayln "-------- SyGuS --------")

; (define hole (?? integer?)) ; same as (??), a hole of type integer

(define-synthax (Start x1 x2 x3 x4 x5 x6 x7 k depth)
  #:base
  (choose
    x1 x2 x3 x4 x5 x6 x7 k
    0 1 2 3 4 5 6 7
  )
  #:else
  (choose
    x1 x2 x3 x4 x5 x6 x7 k
    0 1 2 3 4 5 6 7
    (ite
      (StartBool x1 x2 x3 x4 x5 x6 x7 k (- depth 1))
      (Start x1 x2 x3 x4 x5 x6 x7 k (- depth 1))
      (Start x1 x2 x3 x4 x5 x6 x7 k (- depth 1)))
  )
)
(define-synthax (StartBool x1 x2 x3 x4 x5 x6 x7 k depth)
  #:base (#t)
  #:else
  (choose
    ; ((choose lt le gt ge)
    (lt
      (Start x1 x2 x3 x4 x5 x6 x7 k (- depth 1))
      (Start x1 x2 x3 x4 x5 x6 x7 k (- depth 1))
    )
  )
)

(define (constraint func x1 x2 x3 x4 x5 x6 x7 k)
  (let ([result (interpret (func x1 x2 x3 x4 x5 x6 x7 k))])
    (and
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (< k x1) (= result 0)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (> k x7) (= result 7)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x1) (< k x2)) (= result 1)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x2) (< k x3)) (= result 2)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x3) (< k x4)) (= result 3)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x4) (< k x5)) (= result 4)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x5) (< k x6)) (= result 5)))
(=> (and (< x1 x2) (and (< x2 x3) (and (< x3 x4) (and (< x4 x5) (and (< x5 x6) (< x6 x7)))))) (=> (and (> k x6) (< k x7)) (= result 6)))
    )
  )
)

(define (array-searchn-func x1 x2 x3 x4 x5 x6 x7 k) (Start x1 x2 x3 x4 x5 x6 x7 k 4))
(define M1 (synthesize
            #:forall (list x1 x2 x3 x4 x5 x6 x7 k)
            #:guarantee (assert (constraint array-searchn-func  x1 x2 x3 x4 x5 x6 x7 k))))
(displayln (evaluate (array-searchn-func   x1 x2 x3 x4 x5 x6 x7 k) M1))