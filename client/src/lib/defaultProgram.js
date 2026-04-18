export const DEFAULT_PROGRAM = `shuru
  rakho poora x = 10
  rakho poora y = 5
  
  agar (x > y) {
    likho("x is greater: %d", x)
  } warna {
    likho("y is greater: %d", y)
  }
  
  jabtak (x > 0) {
    likho("x = %d", x)
    x = x - 1
  }
  
  wapas 0
khatam
`;
