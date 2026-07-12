'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Plus, Trash2, GripVertical, Save, X } from 'lucide-react';
import { toast } from 'sonner';

const DATA_TYPES = [
  { value: 'string', label: 'Text' },
  { value: 'integer', label: 'Integer' },
  { value: 'float', label: 'Decimal' },
  { value: 'boolean', label: 'True/False' },
  { value: 'date', label: 'Date' },
  { value: 'datetime', label: 'Date & Time' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone' },
  { value: 'url', label: 'URL' },
  { value: 'uuid', label: 'UUID' },
  { value: 'name', label: 'Person Name' },
  { value: 'address', label: 'Address' },
  { value: 'city', label: 'City' },
  { value: 'country', label: 'Country' },
  { value: 'company', label: 'Company' },
  { value: 'price', label: 'Price' },
];

interface SchemaField {
  name: string;
  type: string;
  description?: string;
  required?: boolean;
  unique?: boolean;
}

interface SchemaEditorProps {
  initialFields: SchemaField[];
  onSave: (fields: SchemaField[]) => Promise<void>;
  onCancel?: () => void;
  readOnly?: boolean;
}

export function SchemaEditor({ initialFields, onSave, onCancel, readOnly = false }: SchemaEditorProps) {
  const [fields, setFields] = useState<SchemaField[]>(initialFields || []);
  const [isSaving, setIsSaving] = useState(false);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  const addField = () => {
    setFields([...fields, { name: '', type: 'string', required: true }]);
    setEditingIndex(fields.length);
  };

  const removeField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index));
    if (editingIndex === index) {
      setEditingIndex(null);
    }
  };

  const updateField = (index: number, updates: Partial<SchemaField>) => {
    const newFields = [...fields];
    newFields[index] = { ...newFields[index], ...updates };
    setFields(newFields);
  };

  const handleSave = async () => {
    // Validate
    const invalidFields = fields.filter(f => !f.name.trim());
    if (invalidFields.length > 0) {
      toast.error('All fields must have a name');
      return;
    }

    setIsSaving(true);
    try {
      await onSave(fields);
      toast.success('Schema updated successfully');
      setEditingIndex(null);
    } catch (error: any) {
      toast.error(error.message || 'Failed to save schema');
    } finally {
      setIsSaving(false);
    }
  };

  const hasChanges = JSON.stringify(fields) !== JSON.stringify(initialFields);

  return (
    <div className="space-y-4">
      {/* Fields List */}
      <div className="space-y-2">
        {fields.map((field, index) => (
          <div
            key={index}
            className={`group p-4 bg-white/5 border border-white/10 rounded-lg transition-all ${
              editingIndex === index ? 'ring-2 ring-teal-500/50' : ''
            }`}
          >
            {editingIndex === index && !readOnly ? (
              /* Edit Mode */
              <div className="space-y-3">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-medium text-zinc-400 mb-1">
                      Field Name <span className="text-red-400">*</span>
                    </label>
                    <Input
                      value={field.name}
                      onChange={(e) => updateField(index, { name: e.target.value })}
                      placeholder="e.g., email, full_name"
                      className="font-mono"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-400 mb-1">
                      Data Type
                    </label>
                    <select
                      value={field.type}
                      onChange={(e) => updateField(index, { type: e.target.value })}
                      className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white text-sm focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-colors"
                    >
                      {DATA_TYPES.map(type => (
                        <option key={type.value} value={type.value} className="bg-zinc-900">
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-zinc-400 mb-1">
                    Description (optional)
                  </label>
                  <Input
                    value={field.description || ''}
                    onChange={(e) => updateField(index, { description: e.target.value })}
                    placeholder="Describe what this field represents"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={field.required || false}
                      onChange={(e) => updateField(index, { required: e.target.checked })}
                      className="w-4 h-4 rounded border-white/20 text-teal-500 focus:ring-teal-500"
                    />
                    Required
                  </label>
                  <label className="flex items-center gap-2 text-sm text-zinc-300 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={field.unique || false}
                      onChange={(e) => updateField(index, { unique: e.target.checked })}
                      className="w-4 h-4 rounded border-white/20 text-teal-500 focus:ring-teal-500"
                    />
                    Unique values
                  </label>
                </div>

                <div className="flex gap-2 pt-2 border-t border-white/10">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => setEditingIndex(null)}
                  >
                    <X className="w-4 h-4 mr-1" />
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => removeField(index)}
                    className="text-red-400 hover:bg-red-500/10"
                  >
                    <Trash2 className="w-4 h-4 mr-1" />
                    Remove
                  </Button>
                </div>
              </div>
            ) : (
              /* View Mode */
              <div 
                className="flex items-center gap-3 cursor-pointer"
                onClick={() => !readOnly && setEditingIndex(index)}
              >
                {!readOnly && (
                  <GripVertical className="w-4 h-4 text-zinc-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <code className="text-sm font-semibold text-white">{field.name}</code>
                    <Badge variant="outline" className="text-xs">
                      {DATA_TYPES.find(t => t.value === field.type)?.label || field.type}
                    </Badge>
                    {field.required && (
                      <Badge variant="outline" className="text-xs text-red-400 border-red-400/30">
                        Required
                      </Badge>
                    )}
                    {field.unique && (
                      <Badge variant="outline" className="text-xs text-blue-400 border-blue-400/30">
                        Unique
                      </Badge>
                    )}
                  </div>
                  {field.description && (
                    <p className="text-xs text-zinc-400">{field.description}</p>
                  )}
                </div>
                {!readOnly && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeField(index);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </Button>
                )}
              </div>
            )}
          </div>
        ))}

        {fields.length === 0 && (
          <div className="text-center py-8 text-zinc-500">
            No fields defined. Add your first field to get started.
          </div>
        )}
      </div>

      {/* Actions */}
      {!readOnly && (
        <div className="flex items-center gap-3 pt-4 border-t border-white/10">
          <Button variant="outline" onClick={addField} className="flex-1">
            <Plus className="w-4 h-4 mr-2" />
            Add Field
          </Button>
          {hasChanges && (
            <>
              {onCancel && (
                <Button variant="ghost" onClick={onCancel}>
                  Cancel
                </Button>
              )}
              <Button
                variant="gradient"
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1"
              >
                {isSaving ? (
                  <>Saving...</>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Schema
                  </>
                )}
              </Button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
