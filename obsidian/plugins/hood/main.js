'use strict';

// Plain CommonJS using Obsidian's bundled modules. No build or package install.
const { Plugin, PluginSettingTab, Setting } = require('obsidian');
const { ViewPlugin } = require('@codemirror/view');

const ENABLED_CLASS = 'hood-custom-cursor';
const ACTIVE_CLASS = 'hood-cursor-active';

class HoodCaret {
  constructor(view, plugin) {
    this.view = view;
    this.plugin = plugin;
    this.destroyed = false;
    // Use the editor's document so secondary windows get the right element.
    this.bar = view.dom.ownerDocument.createElement('div');
    this.bar.className = 'hood-cursor-bar';
    this.bar.style.display = 'none';
    view.scrollDOM.appendChild(this.bar);
    plugin.carets.add(this);
    this.schedule();
  }

  update(update) {
    if (update.selectionSet || update.docChanged || update.geometryChanged ||
        update.focusChanged || update.viewportChanged) this.schedule();
  }

  schedule() {
    if (this.destroyed) return;
    this.view.requestMeasure({
      key: this,
      read: (view) => this.read(view),
      write: (measurement) => this.write(measurement),
    });
  }

  read(view) {
    if (this.destroyed || !this.plugin.active || !this.plugin.settings.customCursor) return null;
    const selection = view.state.selection.main;
    if (!view.hasFocus || !selection.empty) return null;
    try {
      const cursor = view.coordsAtPos(selection.head);
      if (!cursor) return null;
      const scroll = view.scrollDOM;
      const bounds = scroll.getBoundingClientRect();
      const measurement = {
        left: cursor.left - bounds.left + scroll.scrollLeft,
        top: cursor.top - bounds.top + scroll.scrollTop,
        height: cursor.bottom - cursor.top,
      };
      return Object.values(measurement).every(Number.isFinite) && measurement.height > 0
        ? measurement : null;
    } catch (error) {
      // Failed layout must restore the native caret rather than hide both.
      return null;
    }
  }

  write(measurement) {
    if (this.destroyed) return;
    if (!measurement || !this.plugin.active || !this.plugin.settings.customCursor) {
      this.hide();
      return;
    }
    this.plugin.trackDocument(this.view.dom.ownerDocument);
    this.bar.style.left = measurement.left + 'px';
    this.bar.style.top = measurement.top + 'px';
    this.bar.style.height = measurement.height + 'px';
    this.bar.style.display = 'block';
    this.view.contentDOM.classList.add(ACTIVE_CLASS);
  }

  hide() {
    this.bar.style.display = 'none';
    this.view.contentDOM.classList.remove(ACTIVE_CLASS);
  }

  destroy() {
    if (this.destroyed) return;
    this.hide();
    this.bar.remove();
    this.plugin.carets.delete(this);
    this.destroyed = true;
  }
}

class HoodSettingsTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    this.containerEl.empty();
    new Setting(this.containerEl)
      .setName('Custom cursor')
      .setDesc('Use a thick, non-blinking cursor. Turn off to use the native cursor without changing Hood appearance.')
      .addToggle((toggle) => toggle
        .setValue(this.plugin.settings.customCursor)
        .onChange(async (enabled) => {
          // Restore the native caret immediately, even if saving fails.
          this.plugin.setCustomCursor(enabled);
          await this.plugin.saveData(this.plugin.settings);
        }));
  }
}

module.exports = class HoodPlugin extends Plugin {
  async onload() {
    this.carets = new Set();
    this.documents = new Set();
    this.active = true;
    const saved = await this.loadData();
    if (!this.active) return;
    this.settings = { customCursor: typeof saved?.customCursor === 'boolean' ? saved.customCursor : true };
    this.trackDocument(document);
    const plugin = this;
    const extension = ViewPlugin.fromClass(class extends HoodCaret {
      constructor(view) { super(view, plugin); }
    });
    this.registerEditorExtension(extension);
    this.addSettingTab(new HoodSettingsTab(this.app, this));
  }

  trackDocument(ownerDocument) {
    this.documents.add(ownerDocument);
    ownerDocument.body.classList.toggle(ENABLED_CLASS, this.active && this.settings.customCursor);
  }

  setCustomCursor(enabled) {
    this.settings.customCursor = enabled === true;
    for (const ownerDocument of this.documents) this.trackDocument(ownerDocument);
    for (const caret of this.carets) {
      caret.hide();
      if (this.settings.customCursor) caret.schedule();
    }
  }

  onunload() {
    this.active = false;
    for (const caret of this.carets || []) caret.destroy();
    for (const ownerDocument of this.documents || []) ownerDocument.body.classList.remove(ENABLED_CLASS);
    this.documents?.clear();
  }
};
