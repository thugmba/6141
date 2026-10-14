-- Let long inline code wrap in PDF output: allow a line break after , ( [ . = and spaces.
local function esc(s)
  local map = { ["\\"]="\\textbackslash{}", ["{"]="\\{", ["}"]="\\}", ["$"]="\\$", ["&"]="\\&",
                ["#"]="\\#", ["_"]="\\_", ["%"]="\\%", ["~"]="\\textasciitilde{}", ["^"]="\\textasciicircum{}" }
  return (s:gsub("[\\{}$&#_%%~^]", map))
end
function Code(el)
  if not FORMAT:match("latex") then return nil end
  local out = {}
  for ch in el.text:gmatch(utf8.charpattern) do
    local e = esc(ch)
    if ch == " " then e = "\\ " end
    table.insert(out, e)
    if ch:match("[,%(%[%.=_/ ]") then table.insert(out, "\\allowbreak{}") end
  end
  return pandoc.RawInline("latex", "\\texttt{" .. table.concat(out) .. "}")
end
