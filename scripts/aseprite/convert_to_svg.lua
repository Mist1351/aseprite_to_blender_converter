if not app.params['file'] then
    print("Param 'file' is required")
    return 1
end

local filePath = app.params['file']
if not app.command.OpenFile { filename = filePath } then
    print('Filed to load file:', filePath)
    return 1
end

local sprite = app.sprite
if not sprite then
    print("Sprite not found:", sprite.filename)
    return 1
end

if not app.params['output'] then
    print("Output directory is required")
    return 1
end

local output = app.params['output']
local tileWidth = app.params['width']
local tileHeight = app.params['height']

local spriteWidth = sprite.width
local spriteHeight = sprite.height

local numTilesX = math.floor(spriteWidth / tileWidth)
local numTilesY = math.floor(spriteHeight / tileHeight)

for y = 0, numTilesY - 1 do
    for x = 0, numTilesX - 1 do
        local startX = x * tileWidth
        local startY = y * tileHeight
        sprite:crop(startX, startY, tileWidth, tileHeight)

        local svgFileName = string.format("tile_%d_%d.svg", x, y)
        local svgFilePath = app.fs.joinPath(output, svgFileName)

        sprite:saveAs(svgFilePath)
        print("File exported to SVG: " .. svgFilePath)
        app.command.Undo()
    end
end