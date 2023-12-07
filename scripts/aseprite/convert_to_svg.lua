-- Print to stderr
function eprint(...)
    io.stderr:write(table.concat({ ... }, "\t") .. "\n")
end

-- Validate required params
local requiredParams = { 'file', 'output' }
for _, key in ipairs(requiredParams) do
    if not app.params[key] then
        eprint('Param "' .. key .. '" is required!')
        return 1
    end
end

local filePath = app.params['file']
if not app.command.OpenFile { filename = filePath } then
    eprint('Failed to load file: ' .. filePath)
    return 1
end

local sprite = app.sprite
if not sprite then
    eprint('Sprite not found in file: ' .. filePath)
    return 1
end

local spriteWidth = sprite.width
local spriteHeight = sprite.height

local filename = app.fs.fileName(filePath)
local output = app.params['output']
local tileWidth = app.params['width'] or spriteWidth
local tileHeight = app.params['height'] or spriteHeight

local numTilesX = math.floor(spriteWidth / tileWidth)
local numTilesY = math.floor(spriteHeight / tileHeight)

for y = 0, numTilesY - 1 do
    for x = 0, numTilesX - 1 do
        local startX = x * tileWidth
        local startY = y * tileHeight
        sprite:crop(startX, startY, tileWidth, tileHeight)

        local svgFileName = string.format('%s_tile_%d_%d.svg', filename, x, y)
        local svgFilePath = app.fs.joinPath(output, svgFileName)

        if false == sprite:saveAs(svgFilePath) then
            eprint('Failed to save file: ' .. svgFilePath)
            return 1
        end
        print('File exported to SVG: ' .. svgFilePath)
        app.command.Undo()
    end
end