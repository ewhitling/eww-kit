-- Lightweight nvim config: markdown-first, no LSP.
-- Linked into place by `eww install`.

vim.g.mapleader = " "
vim.g.maplocalleader = " "

local opt = vim.opt
opt.number = true
opt.relativenumber = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.expandtab = true
opt.shiftwidth = 2
opt.tabstop = 2
opt.smartindent = true
opt.termguicolors = true
opt.signcolumn = "yes"
opt.cursorline = true
opt.scrolloff = 8
opt.splitright = true
opt.splitbelow = true
opt.ignorecase = true
opt.smartcase = true
opt.undofile = true
opt.swapfile = false
opt.updatetime = 250

-- Markdown-friendly buffers
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "markdown", "text", "gitcommit" },
  callback = function()
    vim.opt_local.wrap = true
    vim.opt_local.linebreak = true
    vim.opt_local.spell = true
    vim.opt_local.conceallevel = 2
  end,
})

-- Treesitter highlighting via Nvim 0.12 built-in parsers
-- (markdown, markdown_inline, lua, vim ship in the runtime, so no plugin is needed).
vim.api.nvim_create_autocmd("FileType", {
  pattern = { "markdown", "lua", "vim" },
  callback = function() pcall(vim.treesitter.start) end,
})

local map = vim.keymap.set
map("n", "<leader>w", "<cmd>w<cr>", { desc = "Save" })
map("n", "<leader>q", "<cmd>q<cr>", { desc = "Quit" })
map("n", "<Esc>", "<cmd>nohlsearch<cr>", { silent = true })
map({ "n", "v" }, "j", "gj")
map({ "n", "v" }, "k", "gk")

-- Bootstrap lazy.nvim
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git", "clone", "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  {
    "shaunsingh/nord.nvim",
    priority = 1000,
    config = function()
      vim.cmd.colorscheme("nord")
    end,
  },
  {
    -- render-markdown uses Nvim 0.12's built-in treesitter + bundled markdown
    -- parsers. No nvim-treesitter plugin needed for this config.
    "MeanderingProgrammer/render-markdown.nvim",
    ft = { "markdown" },
    opts = {
      heading = { icons = { "# ", "## ", "### ", "#### ", "##### ", "###### " } },
      bullet  = { icons = { "•", "◦", "▪", "▫" } },
      checkbox = {
        unchecked = { icon = "[ ]" },
        checked   = { icon = "[x]" },
      },
    },
  },
  {
    "echasnovski/mini.nvim",
    config = function()
      require("mini.statusline").setup()
      require("mini.pairs").setup()
      require("mini.surround").setup()
      require("mini.comment").setup()
      require("mini.files").setup({
        content = { prefix = function() return "", "" end },
      })
      require("mini.pick").setup()
      vim.keymap.set("n", "<leader>e", "<cmd>lua MiniFiles.open()<cr>", { desc = "File tree" })
      vim.keymap.set("n", "<leader>f", "<cmd>Pick files<cr>",          { desc = "Find files" })
      vim.keymap.set("n", "<leader>g", "<cmd>Pick grep_live<cr>",      { desc = "Grep" })
      vim.keymap.set("n", "<leader>b", "<cmd>Pick buffers<cr>",        { desc = "Buffers" })
    end,
  },
}, { ui = { border = "rounded" }, change_detection = { notify = false } })
