from django import forms
from django.utils.safestring import mark_safe


class RoleColorPickerWidget(forms.TextInput):
    PRESET_COLORS = [
        ("LnX Red", "#dc3545"),
        ("Admin Amber", "#f59e0b"),
        ("Moderator Blue", "#0ea5e9"),
        ("Discord Blurple", "#5865f2"),
        ("VIP Purple", "#8b5cf6"),
        ("Dev Emerald", "#10b981"),
        ("Member Gray", "#6c757d"),
    ]

    def render(self, name, value, attrs=None, renderer=None):
        current_value = value or "#6c757d"
        field_id = (attrs or {}).get("id", f"id_{name}")

        presets_html = ""
        for label, hex_code in self.PRESET_COLORS:
            presets_html += f"""
            <button type="button"
                    data-color="{hex_code}"
                    title="{label} ({hex_code})"
                    onclick="window.selectRolePreset_{field_id}('{hex_code}')"
                    style="width: 26px; height: 26px; border-radius: 6px; background-color: {hex_code};
                            border: 2px solid rgba(255,255,255,0.25); cursor: pointer; padding: 0;">
            </button>
            """

        html = f"""
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px;">
            <!-- Preset Role Swatches -->
            <div style="display: flex; align-items: center; gap: 6px; padding: 4px 8px;
                        border: 1px solid #444; border-radius: 8px; background: rgba(128,128,128,0.08);">
                <span style="font-size: 11px; opacity: 0.75; margin-right: 2px;">Presets:</span>
                {presets_html}
            </div>

            <!-- Native Color Picker + Hex Input -->
            <div style="display: flex; align-items: center; gap: 6px;">
                <input type="color"
                        id="{field_id}_picker"
                        value="{current_value}"
                        oninput="window.selectRolePreset_{field_id}(this.value)"
                        style="width: 38px; height: 34px; padding: 2px; border-radius: 6px;
                                border: 1px solid #555; background: transparent; cursor: pointer;">
                <input type="text"
                        name="{name}"
                        id="{field_id}"
                        value="{current_value}"
                        maxlength="7"
                        oninput="window.syncRoleHex_{field_id}(this.value)"
                        style="width: 92px; font-family: monospace; text-transform: uppercase;">
            </div>

            <!-- Live Badge Preview -->
            <span id="{field_id}_preview"
                    style="display: inline-block; padding: 4px 10px; border-radius: 6px;
                        font-size: 12px; font-weight: 600; background-color: {current_value}; color: #fff;">
                Role Preview
            </span>
        </div>

        <script>
            (function() {{
                function getContrastText(hex) {{
                    const clean = hex.replace('#', '');
                    if (clean.length !== 6) return '#ffffff';
                    const r = parseInt(clean.substr(0, 2), 16);
                    const g = parseInt(clean.substr(2, 2), 16);
                    const b = parseInt(clean.substr(4, 2), 16);
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    return luminance > 0.6 ? '#121417' : '#ffffff';
                }}

                function updatePreview(hex) {{
                    const preview = document.getElementById('{field_id}_preview');
                    if (preview && /^#[0-9A-Fa-f]{{6}}$/.test(hex)) {{
                        preview.style.backgroundColor = hex;
                        preview.style.color = getContrastText(hex);
                    }}
                }}

                window.selectRolePreset_{field_id} = function(hex) {{
                    const textInput = document.getElementById('{field_id}');
                    const pickerInput = document.getElementById('{field_id}_picker');
                    if (textInput) textInput.value = hex.toUpperCase();
                    if (pickerInput) pickerInput.value = hex;
                    updatePreview(hex);
                }};

                window.syncRoleHex_{field_id} = function(val) {{
                    const pickerInput = document.getElementById('{field_id}_picker');
                    if (/^#[0-9A-Fa-f]{{6}}$/.test(val)) {{
                        if (pickerInput) pickerInput.value = val;
                        updatePreview(val);
                    }}
                }};

                updatePreview('{current_value}');
            }})();
        </script>
        """
        return mark_safe(html)