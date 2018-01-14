from clicol import terminal

if terminal == "securecrt":
  from colors_securecrt import colors
else: # fallback to putty
  from colors_putty import colors

ct = dict(
              default               = colors['default'],
              lowalert              = colors['orange'],
              alert                 = colors['lred'],
              highalert             = colors['u_lred'],
              comment               = colors['green'],
              privprompt            = colors['bcyan'],
              nonprivprompt         = colors['green'],
              pager                 = colors['orange'],
              address               = colors['green'],
              good                  = colors['bgreen'],
              interface             = colors['lblue'],
              general_configitem    = colors['purple'],
              general_value         = colors['orange'],
              important_value       = colors['u_cyan'],
              description           = colors['bgreen'],
              trafficrate           = colors['lbrown'],
              droprate              = colors['red'],
             )
