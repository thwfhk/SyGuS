#lang rosette/safe

(require rosette/lib/match)
(require rosette/lib/angelic)
(require rosette/lib/synthax)

;;; DSL
(define-symbolic x1 x2 x3 x4 x5 integer?)

; The syntax of the DSL.
(struct plus1 (left right) #:transparent)
(struct minus1 (left right) #:transparent)
(struct ite (bool left right) #:transparent)
(struct and1 (left right) #:transparent)
(struct or1 (left right) #:transparent)
(struct not1 (term) #:transparent)
(struct le (left right) #:transparent)
(struct eq1 (left right) #:transparent)
(struct ge1 (left right) #:transparent)

; The semantics of the DSL.
(define (interpret p)
  (match p
    [(plus1 a b) (+ (interpret a) (interpret b))]
    [(minus1 a b) (- (interpret a) (interpret b))]
    [(ite c a b) (if (interpret c) (interpret a) (interpret b))]
    [(and1 a b) (and (interpret a) (interpret b))]
    [(or1 a b) (or (interpret a) (interpret b))]
    [(not1 a) (not (interpret a))]
    [(le a b) (<= (interpret a) (interpret b))]
    [(eq1 a b) (= (interpret a) (interpret b))]
    [(ge1 a b) (>= (interpret a) (interpret b))]
    [_ p]))

; (define (ans i1 i2) (ite1 (le1 i1 i2) i2 i1))
; (displayln (interpret (ans 5 4)))

;;; SyGuS
(displayln "-------- SyGuS --------")

; (define hole (?? integer?)) ; same as (??), a hole of type integer

(define-synthax (Start x1 x2 x3 x4 x5 depth)
  #:base (choose x1 x2 x3 x4 x5)
  #:else
  (choose
    x1 x2 x3 x4 x5
    ; 0 1
    ; ((choose plus1 minus1)
    ;   (Start x1 x2 x3 x4 x5 (- depth 1))
    ;   (Start x1 x2 x3 x4 x5 (- depth 1)))
    (ite
      (StartBool x1 x2 x3 x4 x5 (- depth 1))
      (Start x1 x2 x3 x4 x5 (- depth 1))
      (Start x1 x2 x3 x4 x5 (- depth 1)))
  )
)
(define-synthax (StartBool x1 x2 x3 x4 x5 depth)
  #:base (#t)
  #:else
  (choose
    ; ((choose and1 or1)
    ;   (StartBool x1 x2 x3 x4 x5 (- depth 1))
    ;   (StartBool x1 x2 x3 x4 x5 (- depth 1))
    ; )
    ; (not1
    ;   (StartBool x1 x2 x3 x4 x5 (- depth 1))
    ; )
    ((choose le); eq1 ge1)
      (Start x1 x2 x3 x4 x5 (- depth 1))
      (Start x1 x2 x3 x4 x5 (- depth 1))
    )
  )
)

(define (constraint func x1 x2 x3 x4 x5)
  (let ([result (interpret (func x1 x2 x3 x4 x5))])
    (and (>= result x1)
         (>= result x2)
         (>= result x3)
         (>= result x4)
         (>= result x5)
         (or
          (= result x1)
          (= result x2)
          (= result x3)
          (= result x4)
          (= result x5)
         )
     )
  )
)

(define (maxn-func x1 x2 x3 x4 x5) (Start x1 x2 x3 x4 x5 4))
(define M1 (synthesize
            #:forall (list x1 x2 x3 x4 x5)
            #:guarantee (assert (constraint maxn-func x1 x2 x3 x4 x5))))
(displayln (evaluate (maxn-func x1 x2 x3 x4 x5) M1))