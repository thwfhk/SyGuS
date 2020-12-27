#lang rosette/safe

(require rosette/lib/match)
(require rosette/lib/angelic)
(require rosette/lib/synthax)

;;; DSL
(define-symbolic x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 integer?)

; The syntax of the DSL.
(struct Plus (left right) #:transparent)
(struct Minus (left right) #:transparent)
(struct Ite (bool left right) #:transparent)
(struct And (left right) #:transparent)
(struct Or (left right) #:transparent)
(struct Not (term) #:transparent)
(struct Le (left right) #:transparent)
(struct Eq (left right) #:transparent)
(struct Ge (left right) #:transparent)
(struct Max (left right) #:transparent)

; The semantics of the DSL.
(define (interpret p)
  (match p
    [(Plus a b) (+ (interpret a) (interpret b))]
    [(Minus a b) (- (interpret a) (interpret b))]
    [(Ite c a b) (if (interpret c) (interpret a) (interpret b))]
    [(And a b) (and (interpret a) (interpret b))]
    [(Or a b) (or (interpret a) (interpret b))]
    [(Not a) (not (interpret a))]
    [(Le a b) (<= (interpret a) (interpret b))]
    [(Eq a b) (= (interpret a) (interpret b))]
    [(Ge a b) (>= (interpret a) (interpret b))]
    [(Max a b) (max (interpret a) (interpret b))]
    [_ p]))

;;; SyGuS
(displayln "-------- SyGuS --------")

; (define hole (?? integer?)) ; same as (??), a hole of type integer

(define-synthax (Start x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 depth)
  #:base (choose x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15)
  #:else
  (choose
    x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15
    ; 0 1
    ; ((choose plus1 minus1)
    ;   (Start x1 x2 x3 x4 x5 (- depth 1))
    ;   (Start x1 x2 x3 x4 x5 (- depth 1)))
    ; (ite
    ;   (StartBool x1 x2 x3 x4 x5 (- depth 1))
    ;   (Start x1 x2 x3 x4 x5 (- depth 1))
    ;   (Start x1 x2 x3 x4 x5 (- depth 1)))
    (Max
      (Start x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 (- depth 1))
      (Start x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 (- depth 1)))
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

(define (constraint func x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15)
  (let ([result (interpret (func x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15))])
    (and (>= result x1)
         (>= result x2)
         (>= result x3)
         (>= result x4)
         (>= result x5)
         (>= result x6)
         (>= result x7)
         (>= result x8)
         (>= result x9)
         (>= result x10)
         (>= result x11)
         (>= result x12)
         (>= result x13)
         (>= result x14)
        ;  (>= result x15)
         (or
          (= result x1)
          (= result x2)
          (= result x3)
          (= result x4)
          (= result x5)
          (= result x6)
          (= result x7)
          (= result x8)
          (= result x9)
          (= result x10)
          (= result x11)
          (= result x12)
          (= result x13)
          (= result x14)
          (= result x15)
         )
     )
  )
)

(define (maxn-func x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15)
        (Start x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15 4))
(define M1 (synthesize
            #:forall (list x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15)
            #:guarantee (assert (constraint maxn-func x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15))))
(displayln (evaluate (maxn-func x1 x2 x3 x4 x5 x6 x7 x8 x9 x10 x11 x12 x13 x14 x15) M1))